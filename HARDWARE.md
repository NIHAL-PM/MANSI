# Hardware Reference: Seeed Studio XIAO ESP32S3 Sense

This document serves as the single source of truth for AI agents and developers working in this workspace.

---

## 1. Device Identification & Connection
- **Board Name:** Seeed Studio XIAO ESP32S3 Sense (XIAO ESP32-S3 + Sense Expansion Board)
- **Active COM Port:** `COM9` (Windows)
- **USB Hardware ID:** `USB\VID_303A&PID_1001` (ESP32-S3 native USB-Serial/JTAG)
- **Baud Rate:** `115200` (standard serial monitor)
- **MAC Address:** `ac:27:6e:a8:57:04`

---

## 2. Silicon & Memory Specifications
- **SoC:** Espressif ESP32-S3 (QFN56, silicon rev v0.2)
- **CPU:** Dual-core Xtensa® 32-bit LX7 @ up to 240 MHz (with vector instructions for AI acceleration)
- **Wireless:** 2.4 GHz Wi-Fi (802.11 b/g/n) + Bluetooth 5.0 (LE)
- **Internal Flash:** **8 MB** Quad SPI Flash
- **PSRAM:** **8 MB** Octal Mode (OPI) Embedded PSRAM (AP_3v3)
  > **Crucial:** Always enable PSRAM (`-DBOARD_HAS_PSRAM`) in firmware configurations. Camera framebuffers (SVGA, UXGA) and Edge AI/ML models require this extra RAM.

---

## 3. Onboard Peripherals & GPIO Mapping

The "Sense" add-on board attaches directly to the bottom expansion connector of the XIAO ESP32S3. It includes an OV2640 camera, a digital PDM microphone, and a microSD card slot.

### A. Camera (OV2640 / DVP Interface)
```c
#define CAMERA_MODEL_XIAO_ESP32S3 // Seeed Studio XIAO ESP32S3 Sense
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     10
#define SIOD_GPIO_NUM     40  // SDA (I2C)
#define SIOC_GPIO_NUM     39  // SCL (I2C)

#define Y9_GPIO_NUM       48
#define Y8_GPIO_NUM       11
#define Y7_GPIO_NUM       12
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       16
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM       17
#define Y2_GPIO_NUM       15
#define VSYNC_GPIO_NUM    38
#define HREF_GPIO_NUM     47
#define PCLK_GPIO_NUM     13
```

### B. Digital PDM Microphone (MSM261D3526H1CPM)
- **PDM Data (DIN):** `GPIO 41`
- **PDM Clock (CLK):** `GPIO 42`

### C. MicroSD Card Reader (SPI)
- **Chip Select (CS):** `GPIO 21` *(Shared with User LED)*
- **SPI SCK:** `GPIO 7` (Breakout Header `D8`)
- **SPI MISO:** `GPIO 8` (Breakout Header `D9`)
- **SPI MOSI:** `GPIO 9` (Breakout Header `D10`)

### D. User LED & Buttons
- **User LED:** `GPIO 21` (Active Low)
- **Boot Button:** `GPIO 0` (Hold during plug-in / reset if manual bootloader entry is needed)
- **Reset Button:** Physical RST button on the side of the XIAO board

### E. External Pinout Breakout
| Pin Label | ESP32-S3 GPIO | Analog | Default Function / Bus | Expansion Overlap Note |
|---|---|---|---|---|
| `D0` | `GPIO 1` | A0 | General I/O, ADC | Free |
| `D1` | `GPIO 2` | A1 | General I/O, ADC | Free |
| `D2` | `GPIO 3` | A2 | General I/O, ADC | Free |
| `D3` | `GPIO 4` | A3 | General I/O, ADC | Free |
| `D4` | `GPIO 5` | A4 | I2C SDA | Free |
| `D5` | `GPIO 6` | A5 | I2C SCL | Free |
| `D6` | `GPIO 43` | - | UART TX | Free |
| `D7` | `GPIO 44` | - | UART RX | Free |
| `D8` | `GPIO 7` | A7 | SPI SCK | Shared with MicroSD SCK |
| `D9` | `GPIO 8` | A8 | SPI MISO | Shared with MicroSD MISO |
| `D10` | `GPIO 9` | A9 | SPI MOSI | Shared with MicroSD MOSI |

---

## 4. Development & Build Tools Setup

### Local Host Environment (Windows)
- **Python:** 3.11 (`esptool` v5.3.0 and `pyserial` v3.5 installed)
- **PlatformIO CLI:** Installed at `C:\Users\HP\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\platformio.exe`
- **Flashing Tool:** `python -m esptool --chip esp32s3 --port COM9`

### PlatformIO Configuration (`platformio.ini`)
```ini
[env:seeed_xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino
upload_port = COM9
upload_speed = 921600
monitor_port = COM9
monitor_speed = 115200

; Crucial ESP32-S3 USB CDC and PSRAM flags:
build_flags = 
    -DBOARD_HAS_PSRAM
    -DARDUINO_USB_CDC_ON_BOOT=1
    -DARDUINO_USB_MODE=1
board_build.psram_type = opi
board_build.flash_mode = qio
board_build.partitions = default_8MB.csv
```

### Arduino IDE Settings (if compiling manually)
- **Board:** `XIAO_ESP32S3`
- **PSRAM:** `OPI PSRAM`
- **Flash Size:** `8MB (64Mb)`
- **USB CDC On Boot:** `Enabled` (Required for `Serial.print()` to output over USB)
- **Port:** `COM9`

---

## 5. Bootloader / Recovery Procedure
If the board fails to respond to automatic flashing:
1. Press and hold the **BOOT** button.
2. While holding **BOOT**, press and release the **RESET** button (or unplug and plug back in USB).
3. Release the **BOOT** button.
4. The board will enter ROM bootloader mode on `COM9`, allowing `esptool` or PlatformIO to flash new firmware cleanly.
