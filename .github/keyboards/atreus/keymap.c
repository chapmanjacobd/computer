// this is the style you want to emulate.
// This is the canonical layout file for the Quantum project. If you want to add another keyboard,

#include "atreus.h"

#define _QWERTY  0
#define _YTREWQ  1
#define _IKAPILA  2
#define _IKASHFT  3
#define _FNCTION  5
#define _NINEKEY  6
#define _GAMEQWERTY   7
#define _ROUSES   8
#define _LYRTBL  9

enum custom_keycodes {
  QWERTY = SAFE_RANGE,
  YTREWQ,
  IKAPILA,
  IKASHFT,
  FNCTION,
  NINEKEY,
  GAMEQWERTY,
  ROUSES,
  LYRTBL,
};

//TD Declarations
enum {
  VOM = 0,
  PRN,
  EGT,
  HRD,
  XRD,
  DSH,
  ESC,
  EQE,
  PGN,
  HND,
  COD,
  UND,
  MND,
  F11,
  F12,
  F13,
  F14,
  F15,
  F16,
  F17,
  F18,
  F19,
  F20,
  //unicode_inputctl
  LINUX,
  WIN,
  WINSH,
  OSX,
};

#define _______     KC_TRNS
#define XXXXXXX     KC_NO

// action-TAP for key/mod behavior LT(layer, KC)
#define XK_TAB      LT(_YTREWQ, KC_TAB)

#define XK_SPC      LT(_IKAPILA, KC_SPC)
#define XK_ENT      LT(_IKAPILA, KC_ENT)

#define XK_PGDN     LT(_IKASHFT, KC_PGDN)
#define XK_BSC      LT(_IKASHFT, KC_BSPC)

#define PIPBOY      LT(_FNCTION, KC_BSLS)

#define XK_DEL      LT(_IKASHFT, KC_DEL)
#define XK_ESC      LT(_LYRTBL, KC_ESC)

// mod-TAP for mod/key behavior MT(modkey, KC)
#define ALT_SC      MT(MOD_RALT, KC_SCLN)
#define CTL_SL      MT(MOD_RCTL, KC_SLSH)
#define SFT_APO     MT(MOD_RSFT, KC_QUOT)
#define SFT_Z       MT(MOD_LSFT, KC_Z)

//sticky modifiers
#define KYCTL       OSM(MOD_LCTL)
#define KYSFT       OSM(MOD_LSFT)
#define KYALT       OSM(MOD_LALT)
#define CAKY        OSM(MOD_LCTL | MOD_LALT)

//shortcuts
#define CADEL       LALT(LCTL(KC_DEL))
#define CAINS       LALT(LCTL(KC_INS))
#define TGNKRO      MAGIC_TOGGLE_NKRO

#define NAVCH       LCTL(KC_HOME)
#define NAVCPD      LCTL(KC_PGDN)
#define NAVCPU      LCTL(KC_PGUP)
#define NAVCE       LCTL(KC_END)
#define NAVCU       LCTL(KC_UP)
#define NAVCD       LCTL(KC_DOWN)
#define NAVCL       LCTL(KC_LEFT)
#define NAVCR       LCTL(KC_RGHT)
#define NAVGU       LGUI(KC_UP)
#define NAVGD       LGUI(KC_DOWN)
#define NAVGL       LGUI(KC_LEFT)
#define NAVGR       LGUI(KC_RGHT)

#define KC_NDSH     LCTL(KC_PMNS)
#define KC_MDSH     LALT(LCTL(KC_PMNS))

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

/*
  TAP
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │ Q  │ W  │ F  │ P  │ B  │              │ J  │ L  │ U  │ Y  │ ;  │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ A  │ R  │ S  │ T  │ G  │              │ M  │ N  │ E  │ I  │ O  │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ X  │ C  │ D  │ V  │ Z  ├────┐    ┌────┤ K  │ H  │ ,  │ .  │ /  │
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │SFTn│CTLn│ALTn│ROUS│SPC │BKSP│    │TAB │ENT │PGDN│ '  │ \  │ESC │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
   HOLD
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │    │    │    │    │    │              │    │    │    │    │ALT │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │    │    │    │    │    │              │    │    │    │    │    │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │    │    │    │    │    ├────┐    ┌────┤    │    │    │    │CTL │
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │SFT │CTL │ALT │ROUS│L123│L OH│    │L OH│L123│L!@#│    │L FN│LESC│
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
   DOUBLETAP
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │    │    │    │    │    │              │    │    │    │    │    │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │    │    │    │    │    │              │    │    │    │    │    │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │    │    │    │    │    ├────┐    ┌────┤    │    │    │    │    │
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │OSML│OSML│OSML│NADA│    │    │    │    │    │    │    │    │    │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
*/

// Colemak PB&J (Mod-DH)
[_QWERTY] = KEYMAP( \
     KC_Q,  KC_W,   KC_E,    KC_R,    KC_T,                      KC_Y,     KC_U,     KC_I,    KC_O,    KC_P,  \
     KC_A,  KC_S,   KC_D,    KC_F,    KC_G,                      KC_H,     KC_J,     KC_K,    KC_L,  ALT_SC,  \
    SFT_Z,  KC_X,   KC_C,    KC_V,    KC_B,                      KC_N,     KC_M,  KC_COMM,  KC_DOT,  CTL_SL,  \
    KYCTL, TT(_ROUSES), KYALT, XK_BSC, XK_SPC, XK_TAB, SFT_APO, XK_ENT,  XK_PGDN,  KC_RGUI, PIPBOY,  XK_ESC  \
),

// useful for one-handed typing
[_YTREWQ] = KEYMAP( \
  KC_SCLN,    KC_Y,    KC_U,    KC_L,   KC_J,                      KC_B,    KC_P,    KC_F,    KC_W,    KC_Q,  \
     KC_O,    KC_I,    KC_E,    KC_N,   KC_M,                      KC_G,    KC_T,    KC_S,    KC_R,    KC_A,  \
  KC_SLSH,  KC_DOT, KC_COMM,    KC_H,   KC_K,                      KC_Z,    KC_V,    KC_D,    KC_C,    KC_X,  \
  _______, KC_QUOT, _______, KC_PGDN, KC_ENT, _______, _______,  XK_SPC, KC_PGUP, _______, _______, _______  \
),

/*
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │ 1  │ 2  │ 3  │ 4  │ 5  │              │ 6  │ 7  │ 8  │ 9  │ 0  │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ M  │ V- │ V+ │NEXT│PLAY│              │ ←  │ ↓  │ ↑  │ →  │DASH│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ -  │ =  │ `  │GUI │UNDO├────┐    ┌────┤HOME│END │HOME│INS │ \  │
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │    │    │    │GUI │    │    │    │    │    │GUI │    │    │    │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
*/

[_IKAPILA] = KEYMAP( \
     KC_1,    KC_2,    KC_3,    KC_4,       KC_5,                        KC_6,    KC_7,    KC_8,    KC_9,    KC_0,  \
  KC_MUTE, KC_VOLD, KC_VOLU, TD(MND),    KC_MPLY,                     KC_LEFT, KC_DOWN,   KC_UP, KC_RGHT, TD(DSH),  \
  KC_MINS, KC_PLUS,  KC_GRV, KC_LGUI, LCTL(KC_Z),                     TD(HND), KC_HOME, TD(HND),  KC_INS, KC_BSLS,  \
  _______, _______, _______, KC_LGUI,    _______,  _______, _______,  _______, KC_LGUI, _______, _______, _______  \
),

/*
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │ !  │ @  │ #  │ $  │ %  │              │ ^  │ &  │ *  │ (  │ )  │
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │PSCR│ ←  │ ↓  │ ↑  │ →  │              │NEXT│PGUP│ V+ │ V- │DASH│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ _  │ +  │ ~  │HOME│END ├────┐    ┌────┤ {} │ () │ <> │ [  │ ]  │
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │    │    │    │    │GUI │DEL │    │BKSP│GUI │    │    │    │    │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
*/

[_IKASHFT] =  KEYMAP( \
  KC_EXLM,   KC_AT, KC_HASH,  KC_DLR, KC_PERC,                  KC_CIRC, KC_AMPR, KC_ASTR, KC_LPRN, KC_RPRN,  \
  KC_PSCR, KC_LEFT, KC_DOWN,   KC_UP, KC_RGHT,                  TD(MND), KC_PGUP, KC_VOLU, TD(VOM), KC_MDSH,  \
  KC_UNDS,  KC_EQL, KC_TILD, KC_HOME,  KC_END,                     M(1),    M(0),    M(5), KC_LBRC, KC_RBRC,  \
  _______, _______, _______, _______, KC_LGUI,  KC_DEL, KC_DEL, KC_LGUI, _______, _______, _______, _______  \
),

/*
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │ F1 │ F2 │ F3 │ F4 │ F5 │              │ F6 │ F7 │ F8 │ F9 │ F10│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ F21│ F22│ F23│ F24│PAUS│              │    │SCLK│BOOT│    │NKRO│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │    │    │    │    │    ├────┐    ┌────┤    │    │    │    │CAPS│
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │    │    │    │    │    │    │    │    │    │    │    │    │    │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
*/

[_FNCTION] =  KEYMAP( \
  TD(F11), TD(F12), TD(F13), TD(F14), TD(F15),                     TD(F16), TD(F17), TD(F18), TD(F19), TD(F20),  \
   KC_F21,  KC_F22,  KC_F23,  KC_F24, XXXXXXX,                     XXXXXXX, KC_SLCK, XXXXXXX, XXXXXXX,  TGNKRO,  \
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                     XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, KC_CAPS,  \
  _______, _______, _______, _______, _______,  _______, _______,  _______, _______, _______, _______, _______  \
),

[_GAMEQWERTY] = KEYMAP( \
     KC_P,    KC_Q,    KC_W,    KC_E,    KC_R,                        KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,  \
  KC_SCLN,    KC_A,    KC_S,    KC_D,    KC_F,                        KC_G,    KC_H,    KC_J,    KC_K,    KC_L,  \
  KC_SLSH,    KC_Z,    KC_X,    KC_C,    KC_V,                        KC_B,    KC_N,    KC_M, KC_COMM, TD(COD),  \
  _______, _______, _______, _______, _______,  _______, _______,  _______, _______, _______, _______, _______  \
),

/*
  ┌────┬────┬────┬────┬────┐              ┌────┬────┬────┬────┬────┐
  │!ESC│ 9  │ 8  │ 7  │ 6  │              │    │MW_L│ MU │MW_R│ AC2│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ 0  │ 2  │ 3  │ 4  │ 5  │              │    │ ML │ MD │ MR │ AC1│
  ├────┼────┼────┼────┼────┤              ├────┼────┼────┼────┼────┤
  │ 1  │ 0  │ENT │ () │ M5 ├────┐    ┌────┤    │MW_D│MW_U│    │ AC0│
  ├────┼────┼────┼────┼────┤    │    │    ├────┼────┼────┼────┼────┤
  │    │    │    │    │    │    │    │    │    │    │    │    │    │
  └────┴────┴────┴────┴────┴────┘    └────┴────┴────┴────┴────┴────┘
*/

[_ROUSES] =  KEYMAP( \
  LALT(KC_ESC), KC_9,  KC_8,    KC_7,    KC_6,                        M(1),    M(0), KC_MS_U,    M(0),    M(2),  \
     KC_0,    KC_2,    KC_3,    KC_4,    KC_5,                        M(5), KC_MS_L, KC_MS_D, KC_MS_R, KC_ACL1,  \
     KC_1,    KC_0,  KC_ENT,    M(0), KC_BTN5,                     KC_WH_L, KC_WH_D, KC_WH_U, KC_WH_R,    M(5),  \
  _______, _______, _______, _______, KC_BTN1,  KC_BTN2, KC_BTN2,  KC_BTN1, KC_BTN2, KC_BTN3, KC_ACL0, _______ \
),

//one_ring=2__rule__them-all
[_LYRTBL] =  KEYMAP( \
    LALT(KC_PSCR),         M(4),      KC_PWR,     KC_POWER,        RESET,                            RESET,         KC_R,    KC_E,     KC_I,       LALT(KC_PSCR),  \
     TG(_NINEKEY), TG(_FNCTION), TG(_ROUSES), TG(_IKASHFT), TG(_IKAPILA),                     TG(_IKAPILA),         KC_S,    KC_U,     KC_B,        TG(_NINEKEY),  \
             M(3), TG(_GAMEQWERTY),  XXXXXXX,      XXXXXXX,      XXXXXXX,                          KC_MYCM,      KC_CALC, XXXXXXX, TG(_GAMEQWERTY),         M(3),  \
     TT(_LYRTBL), TG(_FNCTION), TG(_ROUSES), TG(_IKASHFT), TG(_IKAPILA),  _______, _______,  TG(_IKAPILA), TG(_IKASHFT), TG(_ROUSES), TG(_ROUSES),      _______  \
)};

qk_tap_dance_action_t tap_dance_actions[] = {
 [VOM] = ACTION_TAP_DANCE_DOUBLE(KC_VOLD, KC_MUTE),
 [PRN] = ACTION_TAP_DANCE_DOUBLE(KC_LPRN, KC_RPRN),
 [EGT] = ACTION_TAP_DANCE_DOUBLE(KC_LCBR, KC_RCBR),
 [HRD] = ACTION_TAP_DANCE_DOUBLE(KC_LBRC, KC_RBRC),
 [DSH] = ACTION_TAP_DANCE_DOUBLE(KC_NDSH, KC_MDSH),
 [ESC] = ACTION_TAP_DANCE_DOUBLE(KC_ESC,  LALT(KC_F4)),
 [EQE] = ACTION_TAP_DANCE_DOUBLE(KC_EQL,  KC_ENT),
 [UND] = ACTION_TAP_DANCE_DOUBLE(KC_Z,    LCTL(KC_Z)),
 [PGN] = ACTION_TAP_DANCE_DOUBLE(KC_PGDN, KC_PGUP),
 [HND] = ACTION_TAP_DANCE_DOUBLE(KC_HOME, KC_END),
 [COD] = ACTION_TAP_DANCE_DOUBLE(KC_COMM, KC_DOT),
 [MND] = ACTION_TAP_DANCE_DOUBLE(KC_MNXT, KC_MPRV),
 [F11] = ACTION_TAP_DANCE_DOUBLE(KC_F1,   KC_F11),
 [F12] = ACTION_TAP_DANCE_DOUBLE(KC_F2,   KC_F12),
 [F13] = ACTION_TAP_DANCE_DOUBLE(KC_F3,   KC_F13),
 [F14] = ACTION_TAP_DANCE_DOUBLE(KC_F4,   KC_F14),
 [F15] = ACTION_TAP_DANCE_DOUBLE(KC_F5,   KC_F15),
 [F16] = ACTION_TAP_DANCE_DOUBLE(KC_F6,   KC_F16),
 [F17] = ACTION_TAP_DANCE_DOUBLE(KC_F7,   KC_F17),
 [F18] = ACTION_TAP_DANCE_DOUBLE(KC_F8,   KC_F18),
 [F19] = ACTION_TAP_DANCE_DOUBLE(KC_F9,   KC_F19),
 [F20] = ACTION_TAP_DANCE_DOUBLE(KC_F10,  KC_F20),
};

void matrix_init_user(){
  set_unicode_input_mode(UC_LNX);
}

const macro_t *action_get_macro(keyrecord_t *record, uint8_t id, uint8_t opt) {
  if (record->event.pressed) {
    switch(id) {
  case 0:
    return MACRO( D(LSFT), T(9), U(LSFT), D(LSFT), T(0), U(LSFT), T(LEFT), END );
  case 1:
    return MACRO( D(LSFT), T(LBRC), U(LSFT), D(LSFT), T(RBRC), U(LSFT), T(LEFT), END );
  case 2:
    return MACRO( T(LBRC), T(RBRC), T(LEFT), END);
  case 5:
    return MACRO( D(LSFT), T(COMMA), U(LSFT), D(LSFT), T(DOT), U(LSFT), END );
  case 3:
    clear_keyboard();
    return false;
    break;
  case 4:
    return MACRO( D(LSFT), T(SCOLON), U(LSFT), D(LSFT), T(9), U(LSFT), D(LSFT), T(0), U(LSFT), D(LSFT), T(LBRACKET), U(LSFT), D(LSFT), T(9), U(LSFT), D(LSFT), T(SCOLON), U(LSFT), D(LSFT), T(0), U(LSFT), D(LSFT), T(BSLASH), U(LSFT), D(LSFT), T(SCOLON), U(LSFT), D(LSFT), T(7), U(LSFT), D(LSFT), T(RBRACKET), U(LSFT), T(SCOLON), D(LSFT), T(SCOLON), U(LSFT), END );
  case WINSH:
    set_unicode_input_mode(UC_WIN);
    return false;
    break;
  case WIN:
    set_unicode_input_mode(UC_WINC);
    return false;
    break;
  case OSX:
    set_unicode_input_mode(UC_OSX);
    return false;
    break;
   }
  }
 return MACRO_NONE;
};
