# Arrival AVAS unit: what it is and how to bring it into the SRA-16

The unit is an **AVAS** (Acoustic Vehicle Alerting System) from Arrival: the box an electric vehicle uses to make its low-speed warning sound. Its label reads:

- GTIN 08720514400104, CPV 0.8.0;
- E-mark field "10R-XXXXX", an ECE R10 (EMC) approval number never filled in;
- sticker "not flashed".

So this is a **pre-production unit with no firmware**. It has one sealed 12-way Deutsch DT connector (2 rows of 6).

## What we know and what we don't

- **Known:**
  - Units like this run on the vehicle's 12 V.
  - They usually take commands over **CAN** (the vehicle tells them the speed and when to sound).
  - They contain a class-D amplifier, and sometimes the speaker too.
- **Not known:**
  - **The pinout.** Arrival went into administration in 2024, so no datasheet, firmware or flashing tools are available.
  - **The firmware.** With no firmware it will not respond to anything as it stands. Making it work as designed would mean writing new firmware for its microcontroller. That is a reverse-engineering project, not a wiring job.

## The realistic plan

Use it as the **SRA-16's loud alarm sounder** (outside the rack, or in the office next door), by driving its **amplifier and speaker directly** and leaving its microcontroller unused. That needs no firmware.

1. **Look before powering.**
   - Open the case (4 hex screws on the connector face).
   - Photograph both sides of the board.
   - Note the chip markings: the microcontroller, the CAN transceiver (TJA1042/1043 class), the amplifier IC and the voltage regulator.
   - Check whether a speaker is inside, or only output pins to an external speaker.
2. **Find the pins with a meter, unpowered:**
   - ground: continuity to the regulator's ground and the case;
   - battery +12 V: to the regulator input, usually through a diode;
   - CAN-H / CAN-L: to the transceiver's pins 7 and 6;
   - speaker + / -: to the amplifier outputs;
   - any wake or ignition input.

   Write the result into a pin table here.
3. **First power-up:** from a bench supply at 12 V, current-limited to 0.3 A, with a DT06-12S mating plug (on the buy list).
4. **Choose how to drive it:**
   - **Speaker only, or amplifier input reachable:** feed it from the rack node's spare I2S pins through a small I2S amplifier (MAX98357A, 3 W), or tap the amplifier's input. ESPHome can then play alarm tones or short voice messages from Home Assistant.
   - **Amplifier needs its microcontroller:** write minimal firmware (if the microcontroller has an exposed SWD/JTAG header and is a common part), or take the speaker out and use it with the I2S amplifier.

## Where it fits in the system

- **Alarm sounder:** critical rack alarms (too hot, shutdown request, leak) and, with the cameras on the PoE switch, Home Assistant camera events such as a person detected out of hours.
- **Not inside the rack:** the rack is built to keep sound in. Mount it on the outside of the cabinet, or in the office next to the wall grille.

I'll update the drawings and firmware once steps 1-3 have given us the pinout: send photos of both sides of the board and the meter readings.
