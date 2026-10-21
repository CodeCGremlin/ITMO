#ifndef TM1637_H
#define TM1637_H

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "main.h"

// TM1637 defines
#define TM1637_CLK_PIN 6  // PA6
#define TM1637_DIO_PIN 7  // PA7

#define TM1637_CMD1 0x40  // Данные команда: автоматическое увеличение адреса
#define TM1637_CMD2 0xC0  // Адрес команда: установка начального адреса
#define TM1637_CMD3 0x8F  // Управление дисплеем: включить, максимальная яркость

// Коды сегментов (бит 0 = a, ... бит 6 = g, бит 7 = точка)
#define TM1637_SEG_BLANK 0x00
#define TM1637_SEG_MINUS 0x40  // g
#define TM1637_SEG_DP    0x80  // десятичная точка

// Таблица кодов цифр 0-9, A-F
extern const uint8_t digit_codes[16];

// Прототипы функций для TM1637
void tm1637_init(void);
void tm1637_start(void);
void tm1637_stop(void);
void tm1637_write_byte(uint8_t byte);
void tm1637_display_digit(uint8_t digit, uint8_t data);
void tm1637_display_raw(const uint8_t seg[4]);  // seg[0] - крайний левый разряд
void tm1637_display_number(int number);         // -999..9999, выравнивание вправо
void tm1637_clear(void);
void delay_us(uint32_t us);

#endif
