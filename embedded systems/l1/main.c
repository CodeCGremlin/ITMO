#include "main.h"
#include "tm1637.h"
#include "keyboard.h"

/*
 * Калькулятор: два операнда (цифры 0-9), операции + - * /
 *
 *   0-9 - ввод операнда (первая цифра - A, следующая - B, повторный ввод меняет B)
 *   *   - выбор операции по кругу: + -> - -> * -> / -> +
 *   #   - вычислить и показать результат (после результата - сброс)
 *
 * Индикатор при вводе:  [A][op][B][ ]   "_" - значение ещё не введено
 * Символы операций:     +  ->  b,c,g      -  ->  g
 *                       *  ->  b,c,e,f    /  ->  b,e,g
 */

#define SEG_UNDERSCORE 0x08   // сегмент d - "значение не введено"
#define SEG_E          0x79   // E
#define SEG_r          0x50   // r

typedef enum {
  CALC_INPUT,    // ввод операндов и операции
  CALC_RESULT    // на индикаторе результат
} CalcState;

static const char    opChars[4] = {'+', '-', '*', '/'};
static const uint8_t opSeg[4]   = {0x46, 0x40, 0x36, 0x52};

static CalcState calcState = CALC_INPUT;
static int8_t operandA = -1;   // -1 - не введён
static int8_t operandB = -1;
static int8_t opIndex  = -1;   // -1 - операция не выбрана

volatile uint32_t tickCount;
char lastKey;
uint32_t lastScanTime;


void osSystickHandler(void) {
  tickCount++;
}

void initGPIO() {
  // Включаем тактирование GPIOA и GPIOB
  RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

  // Настраиваем PA5 как выход (светодиод, здесь не используется)
  GPIOA->MODER = (GPIOA->MODER & ~(3 << 10)) | (1 << 10);
  GPIOA->OTYPER &= ~(1 << 5);
  GPIOA->OSPEEDR |= (1 << 10);
  GPIOA->BSRR = (1U << (5 + 16));   // светодиод выключен
}

void initUSART2() {
  // Включаем тактирование USART2
  RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

  // Настраиваем PA2 и PA3 в альтернативный режим
  GPIOA->MODER = (GPIOA->MODER & ~(0xF << 4)) | (0xA << 4);
  GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xFF << 8)) | (1 << 8) | (1 << 12);

  // Настраиваем USART2
  USART2->BRR = 417; // 48MHz/115200
  USART2->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void initSysTick() {
  SysTick->LOAD = 47999; // 1ms при 48MHz
  SysTick->VAL = 0;
  SysTick->CTRL = (1 << 2) | (1 << 1) | (1 << 0);
}

int _write(int file, uint8_t *ptr, int len) {
  for (int i = 0; i < len; i++) {
    while (!(USART2->ISR & USART_ISR_TXE));
    USART2->TDR = ptr[i];
  }
  return len;
}

// Показать вводимое выражение: [A][op][B][ ]
static void showInput(void) {
  uint8_t seg[4] = {TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK};

  seg[0] = (operandA >= 0) ? digit_codes[operandA] : SEG_UNDERSCORE;
  seg[1] = (opIndex  >= 0) ? opSeg[opIndex]        : SEG_UNDERSCORE;
  seg[2] = (operandB >= 0) ? digit_codes[operandB] : SEG_UNDERSCORE;

  tm1637_display_raw(seg);
}

// Полный сброс калькулятора
static void calcReset(void) {
  operandA = -1;
  operandB = -1;
  opIndex  = -1;
  calcState = CALC_INPUT;
  showInput();
}

// Вывод ошибки "Err"
static void showError(void) {
  const uint8_t seg[4] = {SEG_E, SEG_r, SEG_r, TM1637_SEG_BLANK};
  tm1637_display_raw(seg);
}

// Вычисление и вывод результата
static void calcExecute(void) {
  int a = operandA;
  int b = operandB;

  switch (opIndex) {
    case 0:  // +
      tm1637_display_number(a + b);
      printf("%d + %d = %d\n", a, b, a + b);
      break;

    case 1:  // -
      tm1637_display_number(a - b);
      printf("%d - %d = %d\n", a, b, a - b);
      break;

    case 2:  // *
      tm1637_display_number(a * b);
      printf("%d * %d = %d\n", a, b, a * b);
      break;

    case 3: {  // /
      if (b == 0) {
        showError();
        printf("%d / %d = Err (division by zero)\n", a, b);
        break;
      }

      // Частное * 100 с округлением, только целочисленная арифметика
      int x100  = (a * 200 + b) / (2 * b);
      int whole = x100 / 100;   // 0..9
      int frac  = x100 % 100;   // 0..99

      if (frac == 0) {
        tm1637_display_number(whole);
      } else {
        uint8_t seg[4] = {TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK};
        if (frac % 10 == 0) {          // один знак после точки: "  d.d"
          seg[2] = digit_codes[whole] | TM1637_SEG_DP;
          seg[3] = digit_codes[frac / 10];
        } else {                        // два знака после точки: " d.dd"
          seg[1] = digit_codes[whole] | TM1637_SEG_DP;
          seg[2] = digit_codes[frac / 10];
          seg[3] = digit_codes[frac % 10];
        }
        tm1637_display_raw(seg);
      }
      printf("%d / %d = %d.%02d\n", a, b, whole, frac);
      break;
    }

    default:
      return;
  }

  calcState = CALC_RESULT;
}

// Обработка нажатой клавиши
static void calcHandleKey(char key) {
  if (key >= '0' && key <= '9') {
    if (calcState == CALC_RESULT) {
      calcReset();                    // новый расчёт
    }
    int digit = key - '0';
    if (operandA < 0) {
      operandA = digit;               // первая цифра - операнд A
    } else {
      operandB = digit;               // дальше - операнд B (можно переввести)
    }
    showInput();
  }
  else if (key == '*') {
    if (calcState == CALC_RESULT) {
      calcReset();                    // новый расчёт
    }
    opIndex = (opIndex + 1) & 3;      // + - * /
    showInput();
    printf("Operation: %c\n", opChars[opIndex]);
  }
  else if (key == '#') {
    if (calcState == CALC_RESULT) {
      calcReset();                    // повторное # очищает результат
    } else if (operandA >= 0 && operandB >= 0 && opIndex >= 0) {
      calcExecute();
    }
    // если введено не всё - игнорируем
  }
}

int main(void) {
  initGPIO();
  initUSART2();
  initSysTick();
  initKeyboard();
  tm1637_init();

  printf("Calculator: digit, * (operation), digit, # (result)\n");
  showInput();

  while (1) {
    char key = scanKeyboard();
    if (key != '\0') {
      calcHandleKey(key);
    }
  }

  return 0;
}
