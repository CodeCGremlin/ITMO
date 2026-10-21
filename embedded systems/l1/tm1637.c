#include "tm1637.h"

// Функция задержки
void delay_us(uint32_t us) {
  // При 48 MHz, 1 цикл ≈ 20.83 нс
  // Эмпирическая задержка (может потребовать калибровки)
  volatile uint32_t cycles = us * 24;
  while (cycles-- > 0) {
    __asm__("nop");
  }
}

// Таблица кодов для 7-сегментного индикатора (0-9, A-F)
const uint8_t digit_codes[16] = {
  0x3F, // 0
  0x06, // 1
  0x5B, // 2
  0x4F, // 3
  0x66, // 4
  0x6D, // 5
  0x7D, // 6
  0x07, // 7
  0x7F, // 8
  0x6F, // 9
  0x77, // A
  0x7C, // b
  0x39, // C
  0x5E, // d
  0x79, // E
  0x71  // F
};

// Инициализация пинов TM1637
void tm1637_init(void) {
  // Тактирование GPIOA включается в initGPIO()

  // Настраиваем PA6 и PA7 как выходы с открытым стоком
  GPIOA->MODER = (GPIOA->MODER & ~(0xF << (TM1637_CLK_PIN * 2))) | (0x5 << (TM1637_CLK_PIN * 2));
  GPIOA->OTYPER |= (1 << TM1637_CLK_PIN) | (1 << TM1637_DIO_PIN);
  GPIOA->OSPEEDR |= (0x3 << (TM1637_CLK_PIN * 2)) | (0x3 << (TM1637_DIO_PIN * 2));

  // Устанавливаем высокий уровень на обоих пинах
  GPIOA->BSRR = (1 << TM1637_CLK_PIN) | (1 << TM1637_DIO_PIN);

  // Инициализация дисплея
  tm1637_start();
  tm1637_write_byte(TM1637_CMD1);
  tm1637_stop();

  tm1637_start();
  tm1637_write_byte(TM1637_CMD3);
  tm1637_stop();

  tm1637_clear();
}

// Начало передачи
void tm1637_start(void) {
  GPIOA->BSRR = (1 << TM1637_DIO_PIN) | (1 << TM1637_CLK_PIN);  // DIO=1, CLK=1
  delay_us(2);
  GPIOA->BRR = (1 << TM1637_DIO_PIN);  // DIO=0
  delay_us(2);
  GPIOA->BRR = (1 << TM1637_CLK_PIN);  // CLK=0
  delay_us(2);
}

// Конец передачи
void tm1637_stop(void) {
  GPIOA->BRR = (1 << TM1637_CLK_PIN);  // CLK=0
  delay_us(2);
  GPIOA->BRR = (1 << TM1637_DIO_PIN);  // DIO=0
  delay_us(2);
  GPIOA->BSRR = (1 << TM1637_CLK_PIN);  // CLK=1
  delay_us(2);
  GPIOA->BSRR = (1 << TM1637_DIO_PIN);  // DIO=1
  delay_us(2);
}

// Запись байта
void tm1637_write_byte(uint8_t byte) {
  for (uint8_t i = 0; i < 8; i++) {
    GPIOA->BRR = (1 << TM1637_CLK_PIN);  // CLK=0
    delay_us(2);

    if (byte & 0x01) {
      GPIOA->BSRR = (1 << TM1637_DIO_PIN);  // DIO=1
    } else {
      GPIOA->BRR = (1 << TM1637_DIO_PIN);  // DIO=0
    }
    delay_us(2);

    GPIOA->BSRR = (1 << TM1637_CLK_PIN);  // CLK=1
    delay_us(2);

    byte >>= 1;
  }

  // Ожидание подтверждения (ACK)
  GPIOA->BRR = (1 << TM1637_CLK_PIN);  // CLK=0
  GPIOA->BSRR = (1 << TM1637_DIO_PIN);  // DIO=1 (отпускаем линию)
  delay_us(2);
  GPIOA->BSRR = (1 << TM1637_CLK_PIN);  // CLK=1
  delay_us(2);

  // Проверку ACK пропускаем для упрощения

  GPIOA->BRR = (1 << TM1637_CLK_PIN);  // CLK=0
  delay_us(2);
}

// Отображение цифры на указанной позиции
void tm1637_display_digit(uint8_t digit, uint8_t data) {
  tm1637_start();
  tm1637_write_byte(TM1637_CMD2 | digit);  // Установка адреса
  tm1637_write_byte(data);                 // Отправка данных
  tm1637_stop();

  // Установка яркости
  tm1637_start();
  tm1637_write_byte(TM1637_CMD3);
  tm1637_stop();
}

// Вывод четырёх произвольных наборов сегментов (seg[0] - крайний левый разряд)
void tm1637_display_raw(const uint8_t seg[4]) {
  tm1637_start();
  tm1637_write_byte(TM1637_CMD1);  // Автоинкремент адреса
  tm1637_stop();

  tm1637_start();
  tm1637_write_byte(TM1637_CMD2);  // Начальный адрес (левый разряд)
  for (uint8_t i = 0; i < 4; i++) {
    tm1637_write_byte(seg[i]);
  }
  tm1637_stop();

  // Включить дисплей, максимальная яркость
  tm1637_start();
  tm1637_write_byte(TM1637_CMD3);
  tm1637_stop();
}

// Отображение целого числа -999..9999 с выравниванием вправо
void tm1637_display_number(int number) {
  uint8_t seg[4] = {TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK, TM1637_SEG_BLANK};
  uint8_t negative = 0;

  if (number < 0) {
    negative = 1;
    number = -number;
    if (number > 999) number = 999;
  } else if (number > 9999) {
    number = 9999;
  }

  int pos = 3;
  do {
    seg[pos--] = digit_codes[number % 10];
    number /= 10;
  } while (number > 0 && pos >= 0);

  if (negative && pos >= 0) {
    seg[pos] = TM1637_SEG_MINUS;
  }

  tm1637_display_raw(seg);
}

// Очистка дисплея
void tm1637_clear(void) {
  const uint8_t blank[4] = {0, 0, 0, 0};
  tm1637_display_raw(blank);
}
