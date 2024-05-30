#include <Servo.h>

Servo servo1;  
Servo servo2;  
Servo servo3;  
Servo servo4;  

  int mov;
  int ang_cl,ang_y,ang_rot,move_step;

void setup() {
  
  // Initialize the servos to the correct pins
  servo1.attach(4); // servo1:::::pin 4
  servo2.attach(5); // servo2:::::pin 5
  servo3.attach(6); // servo3:::::pin 6
  servo4.attach(7); // servo4:::::pin 7

  // initial position
  servo1.write(80);
  servo2.write(80);
  servo3.write(80);
  servo4.write(0);

  ang_rot = 80;
  ang_y = 80;
  ang_cl = 0;

  move_step = 20;

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
  int mov = Serial.parseInt();
    if (mov >= 1 && mov <= 5) {

    switch(mov){
      case 1: //up
        ang_y=ang_y-move_step;
        servo2.write(ang_y); //moves the lower arm up 
        servo3.write(ang_y); //moves the upper arm up
        delay(100);
        break;

      case 2: //right
        ang_rot=ang_rot-move_step;
        servo1.write(ang_rot); //rotates rigth
        delay(100);
        break;

      case 3: //down
        ang_y=ang_y+move_step;
        servo2.write(ang_y); //moves the lower arm down 
        servo3.write(ang_y);//moves the upper arm down
        delay(100);
        break;

      case 4: //left
        ang_rot=ang_rot+move_step;
        servo1.write(ang_rot); //rotates left
        delay(100);
        break;
        
      case 5: //blink
        if (ang_cl == 230){
          ang_cl = 0;
          servo4.write(ang_cl); //closes the claw
          delay(100);
          break;
        }
        else if (ang_cl == 0)
          ang_cl=230;
          servo4.write(ang_cl); //closes the claw
          delay(100);
          break;

      default:
        Serial.println("Invalid number");
        break;
    }
  }
}

