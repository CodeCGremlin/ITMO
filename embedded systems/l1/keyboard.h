#ifndef KEYBOARD_H
#define KEYBOARD_H

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "main.h"

#define KEY_SCAN_PERIOD_MS 20   // период опроса клавиатуры

void initKeyboard(void);
char readKey(void);
// Возвращает символ один раз при нажатии клавиши, иначе '\0'
char scanKeyboard(void);

extern char lastKey;
extern uint32_t lastScanTime;

#endif
