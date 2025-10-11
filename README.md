# ECG & Heart Rate Live Visualization (Python GUI)

This Python application provides a **real-time ECG waveform visualization** and **heart rate monitoring interface** for data transmitted from an **STM32F401CCU6** microcontroller via the **HC-05 Bluetooth module**.

The GUI continuously reads the ECG ADC data and BPM values over serial communication, plots them dynamically using **Matplotlib**, and displays the **heart rate (BPM)** numerically.  
It also includes a **low heart rate alarm** that triggers a warning beep when the BPM falls below a threshold.

---

## Features

- Real-time ECG waveform plotting  
- Heart rate (BPM) display  
- Automatic peak detection (handled in STM32 code)  
- Bluetooth serial communication via HC-05  
- Low BPM audio alarm  
- Connect/Disconnect controls  
- Smooth animated graph using Matplotlib and Tkinter

---

## Hardware Setup Overview

| Component                  | Description                             |
|----------------------------|-----------------------------------------|
| **STM32F401CCU6**          | Main controller collecting ECG data     |
| **AD8232**                 | ECG analog module                       |
| **HC-05 Bluetooth Module** | Sends ECG & BPM data to the PC          |
| **Laptop/PC**              | Runs this visualization                 |

- The STM32 code sends ECG analog readings and BPM values via Bluetooth.  
- The Python script reads these values, displays them as a waveform, and updates the BPM in real time.
---

## Hardware Connection Diagram

```
                +------------------------+
                |     STM32F401CCU6      |
                +------------------------+
                |                        |
                |  PA0  <--- ECG Out ----|--- AD8232 OUTPUT
                |                        |
                |  PA2  ---> HC-05 RXD   |  (STM32 TX -> HC-05 RX)
                |  PA3  <--- HC-05 TXD   |  (STM32 RX <- HC-05 TX)
                |                        |
                |  3.3V -----------------|--- AD8232 VCC
                |  GND  -----------------|--- AD8232 GND
                |                        |
                +------------------------+

                +-------------------+
                | AD8232 ECG Module |
                +-------------------+
                | OUTPUT  --> PA0   |
                | 3.3V    --> 3.3V  |
                | GND     --> GND   |
                +-------------------+

                +--------------------------+
                |  HC-05 Bluetooth Module  |
                +--------------------------+
                | TXD  --> PA3 (STM32 RX)  |
                | RXD  <-- PA2 (STM32 TX)  |
                | VCC  --> 5V              |
                | GND  --> GND             |
                +--------------------------+
```

## Software Requirements

- **Python 3.8+**
- **Pip** (Python package manager)
- **Keil uVision5** (STM32 Devvelopment Environment)
---

## Install Required Dependencies

Open a terminal (or Command Prompt) and install the following:

```bash
pip install pyserial matplotlib numpy
````

> `winsound` and `tkinter` come preinstalled with Python on Windows.

---

## Find Your Bluetooth COM Port (HC-05)

1. Open **Device Manager** in Windows (`Win + X` → Device Manager).
2. Expand the **Ports (COM & LPT)** section.
3. Look for **“HC-05 Bluetooth Serial Port”** or **“Standard Serial over Bluetooth link”**.
4. Note the **COM Port number** (e.g., `COM4` or `COM7`).
5. Update the line below in your Python code to match your COM port:

   ```python
   SERIAL_PORT = 'COM4'
   ```

---

## How to Run the Program

1. Ensure your STM32 + AD8232 + HC-05 setup is powered and paired via Bluetooth.

2. Open Keil uVision5 -> Create new project -> Select **STM32F401CCU6** -> CMSIS:CORE,Device:Startup -> Finish.

3. Save the C file below as **ecg.c** in project directory.

4. Flash the board, build the file and load it into the STM32.

5. Save the Python file below as **`visualize.py`**.

6. Press the Reset button present in the STM32.

7. Open a terminal in the same folder and run:

   ```bash
   python visualize.py
   ```

8. In the GUI:

   * Enter your correct **Serial Port** (e.g., `COM4`)
   * Click **Connect**
   * The **live ECG waveform** will appear, and **BPM** will be displayed on the top-right.

9. If the **heart rate** drops below 30 BPM (configurable), a **warning beep** will sound.

---

## Notes

* Ensure that the **STM32 UART baud rate** matches the `BAUD_RATE` set in Python (`9600` by default).

* If the waveform looks noisy, check grounding and electrode placement.

* To modify alarm sensitivity, change:

  ```python
  ALARM_THRESHOLD = 30
  ```

* To adjust the display length, modify:

  ```python
  MAX_POINTS = 100
  ```
---

## Hardware Setup & Python GUI Output

<table>
<tr>
<td>

<img height="260" alt="Wireless ECG Monitoring System with Live Graph Display" src="https://github.com/user-attachments/assets/1c2961ec-e36a-4982-ae14-88e501447ca2" />

*STM32F401CCU6 connected with AD8232 ECG module and HC-05 Bluetooth module.*

</td>
<td>

<img height="400" alt="ECG-reading" src="https://github.com/user-attachments/assets/a451e758-3823-4972-aa01-facc7e73359e" />

*Real-time ECG waveform and heart rate (BPM) displayed on the Python GUI.*

</td>
</tr>
</table>

<br/> 

## Contributors
* [@Sudharsana Saravanan S](https://github.com/SudharsanSaravanan)
* [@Shyam Sundar Raju](https://github.com/Shyam-Sundar-Raju)
* [@Dwarakesh V](https://github.com/Dwarakesh-V)
* [@Amarthya Sujai](https://github.com/Amarthya-afk)
---
