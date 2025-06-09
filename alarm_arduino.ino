const int pinoChave = 2;
const int pinoLedVermelho = 11;
const int pinoLedAmarelo = 10;
const int pinoLedVerde = 9;
const int pinMicro = 6;  // Pino do buzzer ou microfone

// Segmentos: a, b, c, d, e, f, g
const int segA = 1;
const int segB = 3;
const int segC = 4;
const int segD = 5;
const int segE = 7;
const int segF = 11;
const int segG = 13;

// Variável para controlar o estado anterior do botão
bool estadoAnteriorBotao = HIGH;

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(9600);
  
  pinMode(pinoChave, INPUT_PULLUP);
  pinMode(pinoLedVermelho, OUTPUT);
  pinMode(pinoLedAmarelo, OUTPUT);
  pinMode(pinoLedVerde, OUTPUT);
  pinMode(pinMicro, OUTPUT);
  pinMode(segA, OUTPUT);
  pinMode(segB, OUTPUT);
  pinMode(segC, OUTPUT);
  pinMode(segD, OUTPUT);
  pinMode(segE, OUTPUT);
  pinMode(segF, OUTPUT);
  pinMode(segG, OUTPUT);
  
  apagaDisplay();
}

void loop() {
  bool estadoAtualBotao = digitalRead(pinoChave);
  
  // Detecta mudança no estado do botão
  if (estadoAtualBotao != estadoAnteriorBotao) {
    if (estadoAtualBotao == LOW) {
      // Botão pressionado - Alarme ativado
      digitalWrite(pinoLedVerde, LOW);
      digitalWrite(pinoLedVermelho, HIGH);
      digitalWrite(pinoLedAmarelo, LOW);
      digitalWrite(pinMicro, HIGH);
      mostrar9();
      Serial.println("ALARME_ON");
    } else {
      // Botão solto - Alarme desativado
      digitalWrite(pinoLedVerde, HIGH);
      digitalWrite(pinoLedVermelho, LOW);
      digitalWrite(pinoLedAmarelo, LOW);
      digitalWrite(pinMicro, LOW);
      mostrar0();
      Serial.println("ALARME_OFF");
    }
    estadoAnteriorBotao = estadoAtualBotao;
  }
  
  delay(100);
}

void mostrar0() {
  digitalWrite(segA, HIGH);
  digitalWrite(segB, HIGH);
  digitalWrite(segC, HIGH);
  digitalWrite(segD, HIGH);
  digitalWrite(segE, HIGH);
  digitalWrite(segF, LOW);
  digitalWrite(segG, HIGH);
}

void mostrar9() {
  digitalWrite(segA, LOW);
  digitalWrite(segB, HIGH);
  digitalWrite(segC, LOW);
  digitalWrite(segD, LOW);
  digitalWrite(segE, LOW);
  digitalWrite(segF, HIGH);
  digitalWrite(segG, HIGH);
}

void apagaDisplay() {
  digitalWrite(segA, LOW);
  digitalWrite(segB, LOW);
  digitalWrite(segC, LOW);
  digitalWrite(segD, LOW);
  digitalWrite(segE, LOW);
  digitalWrite(segF, LOW);
  digitalWrite(segG, LOW);
} 