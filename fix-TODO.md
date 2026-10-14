# 4diac Übungs-Layout Fix-TODOs (Karten-Optimierung)

Dieses Dokument erfasst alle Übungen, bei denen die Platzierung der Bausteine oder IO-Pins im 4diac-Netzwerk nicht der physischen Pin-Reihenfolge des logiBUS® Mini-Trainers entspricht.

> [!NOTE]
> Auf der physischen Trainingskarte (70 mm × 90 mm) sind die digitalen Eingänge **I1 bis I8 links** fest von oben (1,0 cm) nach unten (8,0 cm) angeordnet, und die Ausgänge **Q1 bis Q8 rechts** von 1,0 cm bis 8,0 cm.
> Wenn in 4diac ein Eingang mit höherer Nummer (z. B. I3) weiter oben gezeichnet ist als ein kleinerer (z. B. I1), oder ein daran angeschlossener Baustein ganz oben platziert ist, müssen Verbindungslinien unschön über andere Leitungen kreuzen.
> Sobald die betroffenen FBs in der 4diacIDE nach unten verschoben und gespeichert werden, erzeugt der Generator beim nächsten Durchlauf automatisch ein sauberes, kreuzungsfreies Kartenlayout!

## Übersicht
- **Geprüfte Übungen:** 496
- **Übungen mit Optimierungsbedarf:** 43

---

## Offene Layout-TODOs

- [ ] **Uebung_003a2b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_003a2b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2000) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=-800)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2000) liegt oberhalb von I2 (`DigitalInput_CLK_I2`, y=200)
  - Baustein unglücklich platziert: `AX_SPLIT_2` (AX_SPLIT_2, verbunden mit I3) liegt bei y=-1600 oberhalb von `AX_FB_R_IO_Q1` (AX_FB_R_IO, verbunden mit I1, y=-500). Empfehlung: `AX_SPLIT_2` in 4diac nach unten verschieben (unterhalb von `AX_FB_R_IO_Q1`, z.B. y > -500).
  - Baustein unglücklich platziert: `AX_SPLIT_2` (AX_SPLIT_2, verbunden mit I3) liegt bei y=-1600 oberhalb von `AX_FB_R_IO_Q2` (AX_FB_R_IO, verbunden mit I2, y=500). Empfehlung: `AX_SPLIT_2` in 4diac nach unten verschieben (unterhalb von `AX_FB_R_IO_Q2`, z.B. y > 500).

- [ ] **Uebung_004a4_AX_T** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_004a4_AX_T.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_CLK`, y=-800) liegt oberhalb von I1 (`DigitalInput_RST`, y=300)

- [ ] **Uebung_006_SAFE_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_006_SAFE_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I8 (`StopFeedback`, y=2000) liegt oberhalb von I7 (`ResetInput`, y=2900)
  - Baustein unglücklich platziert: `StartPermit` (E_RS, verbunden mit I8) liegt bei y=1900 oberhalb von `ResetButton` (SF_ResetButton, verbunden mit I7, y=3100). Empfehlung: `StartPermit` in 4diac nach unten verschieben (unterhalb von `ResetButton`, z.B. y > 3100).
  - Baustein unglücklich platziert: `MainSR` (AX_SR, verbunden mit I8) liegt bei y=900 oberhalb von `ResetButton` (SF_ResetButton, verbunden mit I7, y=3100). Empfehlung: `MainSR` in 4diac nach unten verschieben (unterhalb von `ResetButton`, z.B. y > 3100).

- [ ] **Uebung_006_SAFE_AX_02** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_006_SAFE_AX_02.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I8 (`EStopFeedback`, y=2000) liegt oberhalb von I7 (`ResetInput`, y=3300)
  - Baustein unglücklich platziert: `EmergencyStop` (SF_EmergencyStop, verbunden mit I8) liegt bei y=2300 oberhalb von `ResetButton` (SF_ResetButton, verbunden mit I7, y=3500). Empfehlung: `EmergencyStop` in 4diac nach unten verschieben (unterhalb von `ResetButton`, z.B. y > 3500).
  - Baustein unglücklich platziert: `MainSR` (AX_SR, verbunden mit I8) liegt bei y=1000 oberhalb von `ResetButton` (SF_ResetButton, verbunden mit I7, y=3500). Empfehlung: `MainSR` in 4diac nach unten verschieben (unterhalb von `ResetButton`, z.B. y > 3500).

- [ ] **Uebung_006a2_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_006a2_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2100) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=-900)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2100) liegt oberhalb von I2 (`DigitalInput_CLK_I2`, y=100)
  - Baustein unglücklich platziert: `AX_T_FF_SR_Q1` (AX_T_FF_SR, verbunden mit I3) liegt bei y=-900 oberhalb von `AX_T_FF_SR_Q2` (AX_T_FF_SR, verbunden mit I2, y=100). Empfehlung: `AX_T_FF_SR_Q1` in 4diac nach unten verschieben (unterhalb von `AX_T_FF_SR_Q2`, z.B. y > 100).

- [ ] **Uebung_006a2b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_006a2b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2000) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=-900)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=-2000) liegt oberhalb von I2 (`DigitalInput_CLK_I2`, y=100)
  - Baustein unglücklich platziert: `AX_SPLIT_2` (AX_SPLIT_2, verbunden mit I3) liegt bei y=-1600 oberhalb von `AX_T_FF_SR_Q1` (AX_FB_RS_T_FF, verbunden mit I1, y=-700). Empfehlung: `AX_SPLIT_2` in 4diac nach unten verschieben (unterhalb von `AX_T_FF_SR_Q1`, z.B. y > -700).
  - Baustein unglücklich platziert: `AX_SPLIT_2` (AX_SPLIT_2, verbunden mit I3) liegt bei y=-1600 oberhalb von `AX_T_FF_SR_Q2` (AX_FB_RS_T_FF, verbunden mit I2, y=300). Empfehlung: `AX_SPLIT_2` in 4diac nach unten verschieben (unterhalb von `AX_T_FF_SR_Q2`, z.B. y > 300).

- [ ] **Uebung_006c_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_006c_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q6 (`DigitalOutput_Q6`, y=5020) liegt oberhalb von Q5 (`DigitalOutput_Q5`, y=6266.67)

- [ ] **Uebung_019b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_019b_AX.SUB`)
  - Baustein unglücklich platziert: `Select_4_AUI` (AUI_AUI_MUX_4_VAL, verbunden mit I2) liegt bei y=-300 oberhalb von `AX_SR` (AX_SR, verbunden mit I1, y=1800). Empfehlung: `Select_4_AUI` in 4diac nach unten verschieben (unterhalb von `AX_SR`, z.B. y > 1800).
  - Baustein unglücklich platziert: `Select_4_AUI` (AUI_AUI_MUX_4_VAL, verbunden mit I3) liegt bei y=-300 oberhalb von `AX_SR` (AX_SR, verbunden mit I2, y=1800). Empfehlung: `Select_4_AUI` in 4diac nach unten verschieben (unterhalb von `AX_SR`, z.B. y > 1800).
  - Baustein unglücklich platziert: `Select_4_AUI` (AUI_AUI_MUX_4_VAL, verbunden mit I3) liegt bei y=-300 oberhalb von `AX_SR` (AX_SR, verbunden mit I1, y=1800). Empfehlung: `Select_4_AUI` in 4diac nach unten verschieben (unterhalb von `AX_SR`, z.B. y > 1800).

- [ ] **Uebung_019c_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_019c_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`ACK`, y=1500) liegt oberhalb von I3 (`Alarmeingang`, y=2600)
  - Baustein unglücklich platziert: `AX_E_PERMIT_INVERT_1` (AX_E_PERMIT_INVERT_3, verbunden mit I4) liegt bei y=-200 oberhalb von `AX_SPLIT_4` (AX_SPLIT_2, verbunden mit I3, y=3100). Empfehlung: `AX_E_PERMIT_INVERT_1` in 4diac nach unten verschieben (unterhalb von `AX_SPLIT_4`, z.B. y > 3100).

- [ ] **Uebung_028a2_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028a2_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028a_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028a_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028a_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028a_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028b2_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028b2_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=-100) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=400)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028b_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028b_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=-200) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=400)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I4) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028c2_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028c2_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I7 (`AnalogInput_I4`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=-300) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=400)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028c3_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028c3_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I7 (`AnalogInput_I7`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=-300) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=400)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_028c_AR** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_028c_AR.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I7 (`AnalogInput_I7`, y=1900) liegt oberhalb von I3 (`DigitalInput_I3_CS`, y=2500)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=-300) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=400)
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I2, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).
  - Baustein unglücklich platziert: `AD_TO_AUDI` (AD_TO_AUDI, verbunden mit I7) liegt bei y=900 oberhalb von `CALIBRATE` (AR_CALIBRATE, verbunden mit I3, y=1500). Empfehlung: `AD_TO_AUDI` in 4diac nach unten verschieben (unterhalb von `CALIBRATE`, z.B. y > 1500).

- [ ] **Uebung_031_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_031_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_CLK_I2`, y=-500) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=600)
  - Baustein unglücklich platziert: `strip_set_pixel` (strip_set_pixel, verbunden mit I2) liegt bei y=500 oberhalb von `hsv2rgb` (hsv2rgb, verbunden mit I1, y=800). Empfehlung: `strip_set_pixel` in 4diac nach unten verschieben (unterhalb von `hsv2rgb`, z.B. y > 800).

- [ ] **Uebung_040_2_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_040_2_AX.SUB`)
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I2) liegt bei y=-3493.33 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3493.33 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3493.33 oberhalb von `E_CTU_1` (AUI_CTU, verbunden mit I3, y=-1360). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `E_CTU_1`, z.B. y > -1360).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I3) liegt bei y=-1360 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I4) liegt bei y=-1360 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).

- [ ] **Uebung_040_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_040_AX.SUB`)
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I2) liegt bei y=-3433.33 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3433.33 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3433.33 oberhalb von `E_CTU_1` (AUI_CTU, verbunden mit I3, y=-1300). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `E_CTU_1`, z.B. y > -1300).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I3) liegt bei y=-1300 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I4) liegt bei y=-1300 oberhalb von `loop` (sequence_E_08_loop_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `loop`, z.B. y > -600).

- [ ] **Uebung_059_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_059_AX.SUB`)
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I2) liegt bei y=-3533.33 oberhalb von `sequence_block` (sequence_E_08_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `sequence_block`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3533.33 oberhalb von `E_CTU_1` (AUI_CTU, verbunden mit I3, y=-1400). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `E_CTU_1`, z.B. y > -1400).
  - Baustein unglücklich platziert: `E_CTU_0` (AUI_CTU, verbunden mit I4) liegt bei y=-3533.33 oberhalb von `sequence_block` (sequence_E_08_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_0` in 4diac nach unten verschieben (unterhalb von `sequence_block`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I3) liegt bei y=-1400 oberhalb von `sequence_block` (sequence_E_08_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `sequence_block`, z.B. y > -600).
  - Baustein unglücklich platziert: `E_CTU_1` (AUI_CTU, verbunden mit I4) liegt bei y=-1400 oberhalb von `sequence_block` (sequence_E_08_AX, verbunden mit I1, y=-600). Empfehlung: `E_CTU_1` in 4diac nach unten verschieben (unterhalb von `sequence_block`, z.B. y > -600).

- [ ] **Uebung_087_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_087_AX.SUB`)
  - Baustein unglücklich platziert: `AX_X_TO_BOOL_2` (AX_X_TO_BOOL, verbunden mit I2) liegt bei y=2300 oberhalb von `E_DEMUX` (E_DEMUX, verbunden mit I1, y=2900). Empfehlung: `AX_X_TO_BOOL_2` in 4diac nach unten verschieben (unterhalb von `E_DEMUX`, z.B. y > 2900).

- [ ] **Uebung_087a1_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_087a1_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_I2`, y=2300) liegt oberhalb von I1 (`DigitalInput_I4`, y=4700)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_I3`, y=3500) liegt oberhalb von I1 (`DigitalInput_I4`, y=4700)
  - Baustein unglücklich platziert: `AX_X_TO_BOOL_2` (AX_X_TO_BOOL, verbunden mit I2) liegt bei y=2300 oberhalb von `E_DEMUX_4` (E_DEMUX_4, verbunden mit I1, y=2900). Empfehlung: `AX_X_TO_BOOL_2` in 4diac nach unten verschieben (unterhalb von `E_DEMUX_4`, z.B. y > 2900).
  - Baustein unglücklich platziert: `AX_X_TO_BOOL_2` (AX_X_TO_BOOL, verbunden mit I2) liegt bei y=2300 oberhalb von `AX_X_TO_BOOL_4` (AX_X_TO_BOOL, verbunden mit I1, y=4700). Empfehlung: `AX_X_TO_BOOL_2` in 4diac nach unten verschieben (unterhalb von `AX_X_TO_BOOL_4`, z.B. y > 4700).
  - Baustein unglücklich platziert: `AX_X_TO_BOOL_3` (AX_X_TO_BOOL, verbunden mit I3) liegt bei y=3500 oberhalb von `AX_X_TO_BOOL_4` (AX_X_TO_BOOL, verbunden mit I1, y=4700). Empfehlung: `AX_X_TO_BOOL_3` in 4diac nach unten verschieben (unterhalb von `AX_X_TO_BOOL_4`, z.B. y > 4700).

- [ ] **Uebung_090a1_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_090a1_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_I4`, y=3100) liegt oberhalb von I1 (`DigitalInput_I1`, y=4400)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_I4`, y=3100) liegt oberhalb von I2 (`DigitalInput_I2`, y=5500)

- [ ] **Uebung_090a2_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_090a2_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_I4`, y=3300) liegt oberhalb von I1 (`DigitalInput_I1`, y=4400)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_I4`, y=3300) liegt oberhalb von I2 (`DigitalInput_I2`, y=5600)

- [ ] **Uebung_094_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_094_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_CLK_I2`, y=-800) liegt oberhalb von I1 (`DigitalInput_I1`, y=200)

- [ ] **Uebung_095_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_095_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_CLK_I2`, y=-800) liegt oberhalb von I1 (`DigitalInput_I1`, y=1200)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_CLK_I3`, y=200) liegt oberhalb von I1 (`DigitalInput_I1`, y=1200)

- [ ] **Uebung_104_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_104_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I4 (`Reset_Button`, y=-2100) liegt oberhalb von I1 (`Feedback_S1`, y=-1000)
  - Pin-Reihenfolge invertiert: Eingang I4 (`Reset_Button`, y=-2100) liegt oberhalb von I2 (`Feedback_S2`, y=0)
  - Pin-Reihenfolge invertiert: Eingang I4 (`Reset_Button`, y=-2100) liegt oberhalb von I3 (`Feedback_S3`, y=1000)

- [ ] **Uebung_152_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_152_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_I2`, y=0) liegt oberhalb von I1 (`DigitalInput_I1`, y=2300)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_I3`, y=1000) liegt oberhalb von I1 (`DigitalInput_I1`, y=2300)
  - Pin-Reihenfolge invertiert: Eingang I8 (`logiBUS_PI_IDA`, y=400) liegt oberhalb von I1 (`DigitalInput_I1`, y=2300)
  - Pin-Reihenfolge invertiert: Eingang I8 (`logiBUS_PI_IDA`, y=400) liegt oberhalb von I3 (`DigitalInput_I3`, y=1000)
  - Baustein unglücklich platziert: `E_CYCLE` (E_CYCLE, verbunden mit I2) liegt bei y=500 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2500). Empfehlung: `E_CYCLE` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2500).
  - Baustein unglücklich platziert: `E_CYCLE` (E_CYCLE, verbunden mit I3) liegt bei y=500 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2500). Empfehlung: `E_CYCLE` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2500).
  - Baustein unglücklich platziert: `AD_TO_AR_NUM` (AD_TO_AR_NUM, verbunden mit I8) liegt bei y=400 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2500). Empfehlung: `AD_TO_AR_NUM` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2500).

- [ ] **Uebung_153_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_153_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_I2`, y=0) liegt oberhalb von I1 (`DigitalInput_I1`, y=2200)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_I3`, y=1000) liegt oberhalb von I1 (`DigitalInput_I1`, y=2200)
  - Pin-Reihenfolge invertiert: Eingang I8 (`logiBUS_PI_IDA`, y=400) liegt oberhalb von I1 (`DigitalInput_I1`, y=2200)
  - Pin-Reihenfolge invertiert: Eingang I8 (`logiBUS_PI_IDA`, y=400) liegt oberhalb von I3 (`DigitalInput_I3`, y=1000)
  - Baustein unglücklich platziert: `E_CYCLE` (E_CYCLE, verbunden mit I2) liegt bei y=500 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2300). Empfehlung: `E_CYCLE` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2300).
  - Baustein unglücklich platziert: `E_CYCLE` (E_CYCLE, verbunden mit I3) liegt bei y=500 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2300). Empfehlung: `E_CYCLE` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2300).
  - Baustein unglücklich platziert: `AD_TO_AR_NUM` (AD_TO_AR_NUM, verbunden mit I8) liegt bei y=1100 oberhalb von `AX_T_FF` (AX_T_FF, verbunden mit I1, y=2300). Empfehlung: `AD_TO_AR_NUM` in 4diac nach unten verschieben (unterhalb von `AX_T_FF`, z.B. y > 2300).

- [ ] **Uebung_160_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_160_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`DigitalOutput_Q56`, y=300) liegt oberhalb von Q6 (`DigitalOutput_Q6`, y=1400)

- [ ] **Uebung_160b2_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_160b2_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`DigitalOutput_Q56`, y=300) liegt oberhalb von Q6 (`DigitalOutput_Q6`, y=1400)

- [ ] **Uebung_160b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_160b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`DigitalOutput_Q56`, y=300) liegt oberhalb von Q6 (`DigitalOutput_Q6`, y=1400)

- [ ] **Uebung_201b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_201b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=300) liegt oberhalb von Q6 (`Linkslauf`, y=1200)

- [ ] **Uebung_202b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_202b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=-300) liegt oberhalb von Q6 (`Linkslauf`, y=600)

- [ ] **Uebung_203b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_203b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=500) liegt oberhalb von Q6 (`Linkslauf`, y=1400)

- [ ] **Uebung_204_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_204_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1900) liegt oberhalb von I1 (`DigitalInput_I1`, y=-800)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1900) liegt oberhalb von I2 (`DigitalInput_I2`, y=200)

- [ ] **Uebung_204b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_204b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1800) liegt oberhalb von I1 (`DigitalInput_I1`, y=-800)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1800) liegt oberhalb von I2 (`DigitalInput_I2`, y=200)
  - Pin-Reihenfolge invertiert: Ausgang Q5 (`Rechtslauf`, y=-800) liegt oberhalb von Q4 (`Trip_Anzeige`, y=1900)
  - Pin-Reihenfolge invertiert: Ausgang Q6 (`Linkslauf`, y=1000) liegt oberhalb von Q4 (`Trip_Anzeige`, y=1900)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=100) liegt oberhalb von Q4 (`Trip_Anzeige`, y=1900)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=100) liegt oberhalb von Q6 (`Linkslauf`, y=1000)

- [ ] **Uebung_204c_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_204c_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1900) liegt oberhalb von I1 (`DigitalInput_I1`, y=-800)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Reset`, y=-1900) liegt oberhalb von I2 (`DigitalInput_I2`, y=200)

- [ ] **Uebung_205b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_205b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Ausgang Q56 (`LowSide_Treiber`, y=-300) liegt oberhalb von Q6 (`Linkslauf`, y=600)

- [ ] **Uebung_206b_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_206b_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Set_I3`, y=-2700) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=-500)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_Reset_I4`, y=-1600) liegt oberhalb von I1 (`DigitalInput_CLK_I1`, y=-500)
  - Pin-Reihenfolge invertiert: Eingang I3 (`DigitalInput_Set_I3`, y=-2700) liegt oberhalb von I2 (`DigitalInput_CLK_I2`, y=600)
  - Pin-Reihenfolge invertiert: Eingang I4 (`DigitalInput_Reset_I4`, y=-1600) liegt oberhalb von I2 (`DigitalInput_CLK_I2`, y=600)
  - Pin-Reihenfolge invertiert: Ausgang Q2 (`DigitalOutput_Q2`, y=300) liegt oberhalb von Q1 (`DigitalOutput_Q1`, y=1300)
  - Baustein unglücklich platziert: `ILOCK_T_FF_SR_1` (ILOCK_T_FF_SR_AX, verbunden mit I3) liegt bei y=-1000 oberhalb von `ILOCK_T_FF_SR_2` (ILOCK_T_FF_SR_AX, verbunden mit I2, y=500). Empfehlung: `ILOCK_T_FF_SR_1` in 4diac nach unten verschieben (unterhalb von `ILOCK_T_FF_SR_2`, z.B. y > 500).
  - Baustein unglücklich platziert: `ILOCK_T_FF_SR_1` (ILOCK_T_FF_SR_AX, verbunden mit I4) liegt bei y=-1000 oberhalb von `ILOCK_T_FF_SR_2` (ILOCK_T_FF_SR_AX, verbunden mit I2, y=500). Empfehlung: `ILOCK_T_FF_SR_1` in 4diac nach unten verschieben (unterhalb von `ILOCK_T_FF_SR_2`, z.B. y > 500).

- [ ] **Uebung_246_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_246_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_I2`, y=1600) liegt oberhalb von I1 (`DigitalInput_I1`, y=1800)

- [ ] **Uebung_248_AX** (`../4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_248_AX.SUB`)
  - Pin-Reihenfolge invertiert: Eingang I2 (`DigitalInput_I2`, y=1400) liegt oberhalb von I1 (`DigitalInput_I1`, y=1700)
