#ifndef USB_DESCRIPTORS_H_
#define USB_DESCRIPTORS_H_

enum {
    REPORT_ID_KEYBOARD = 1
};

// String indices
enum {
    STR_MANUFACTURER = 1,
    STR_PRODUCT,
    STR_SERIAL,
};

// Device descriptor
tud_desc_device_t const desc_device = {
    .bLength            = sizeof(tud_desc_device_t),
    .bDescriptorType    = TUSB_DESC_DEVICE,
    .bcdUSB             = 0x0200,
    .bDeviceClass       = 0x00,
    .bDeviceSubClass    = 0x00,
    .bDeviceProtocol    = 0x00,
    .bMaxPacketSize0    = CFG_TUD_ENDPOINT0_SIZE,
    .idVendor           = 0x2E8A,  // Raspberry Pi VID
    .idProduct          = 0x0003,  // Example PID
    .bcdDevice          = 0x0100,
    .iManufacturer      = STR_MANUFACTURER,
    .iProduct           = STR_PRODUCT,
    .iSerialNumber      = STR_SERIAL,
    .bNumConfigurations = 0x01
};

// HID report descriptor for keyboard
uint8_t const desc_hid_report[] = {
    TUD_HID_REPORT_DESC_KEYBOARD( HID_REPORT_ID(REPORT_ID_KEYBOARD) )
};

// Configuration descriptor (simplified for HID only)
uint8_t const desc_configuration[] = {
    // Config length, type, total length, num interfaces, config num, string index, attributes, power
    9, TUSB_DESC_CONFIGURATION, 34, 1, 1, 0, TUSB_DESC_CONFIG_ATT_BUS_POWERED, 50,

    // Interface: HID
    9, TUSB_DESC_INTERFACE, 0, 0, 1, TUSB_CLASS_HID, HID_SUBCLASS_BOOT, HID_PROTOCOL_KEYBOARD, 0,

    // HID descriptor
    9, HID_DESC_TYPE_HID, 0x0111, 0, 1, HID_DESC_TYPE_REPORT, sizeof(desc_hid_report), 10,

    // Endpoint IN
    7, TUSB_DESC_ENDPOINT, 0x81, TUSB_XFER_INTERRUPT, 8, 10
};

// String descriptors
char const* string_desc_arr[] = {
    (const char[]) { 0x09, 0x04 },  // 0: Language
    "Raspberry Pi",                 // 1: Manufacturer
    "Pico HID Keyboard",            // 2: Product
    "123456",                       // 3: Serial
};

// TinyUSB callbacks
uint16_t const* tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
    (void) langid;
    static uint16_t desc_str[32];
    uint8_t chr_count;

    if (index == 0) {
        memcpy(&desc_str[1], string_desc_arr[0], 2);
        chr_count = 1;
    } else {
        if (index >= sizeof(string_desc_arr)/sizeof(string_desc_arr[0])) return NULL;
        const char* str = string_desc_arr[index];
        chr_count = strlen(str);
        if (chr_count > 31) chr_count = 31;
        for (uint8_t i = 0; i < chr_count; i++) desc_str[1 + i] = str[i];
    }

    desc_str[0] = (TUSB_DESC_STRING << 8) | (2 * chr_count + 2);
    return desc_str;
}

uint8_t const * tud_hid_descriptor_report_cb(uint8_t instance) {
    (void) instance;
    return desc_hid_report;
}

uint8_t const * tud_descriptor_device_cb(void) {
    return (uint8_t const *) &desc_device;
}

uint8_t const * tud_descriptor_configuration_cb(uint8_t index) {
    (void) index;
    return desc_configuration;
}

#endif
