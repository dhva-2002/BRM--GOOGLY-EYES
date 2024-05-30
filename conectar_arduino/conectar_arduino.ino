// V - Vertical Electrodes, H - Horiontal Electrode.

const int analogInPin_V = A1;
const int analogInPin_H = A0;

int sensorValue_V = 0;
int sensorValue_H = 0;

void setup() {
  // Initialize serial communication at 9600 bps.
  Serial.begin(9600);
}

void loop() {
  // Read the analog input value.
  sensorValue_V = analogRead(analogInPin_V);
  sensorValue_H = analogRead(analogInPin_H);

  // Print the results to the serial monitor,
  // delimiting the two values with a comma.
  //Serial.print(900);
  //Serial.print(", ");
  //Serial.print(500);
  //Serial.print(", ");
  Serial.print(sensorValue_V);
  Serial.print(",");
  Serial.println(sensorValue_H);


  // Wait for 2 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading.
  delay(50);
}