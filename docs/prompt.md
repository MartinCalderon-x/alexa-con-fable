# El pedido real

El diseño salió de una conversación con Claude Code (app de escritorio), no de un único mensaje.
Estos son los textos que lo definieron, tal como quedaron en la sesión del 10 de noviembre de 2026.

## 1 · La idea (Martín)

> Vamos a trabajar en crear un reel o quizás un video para YouTube […] mostrando el video del PCB,
> quizás incluso podemos crear algo nosotros en KiCad (lo tengo instalado) haciendo un video paso a
> paso de cómo se crea el circuito, PCB […]. Luego yo hago un voice over en base a un guion.

## 2 · La propuesta de componentes (Claude) y la elección (Martín)

Propuesta:

> Un satélite de voz chico con un ESP32-S3, un micrófono I²S, un amplificador con parlante, un LED
> y USB-C. Se conecta con tu tema de agentes de voz […].

Elección: **«Satélite de voz»**.

Después Martín cambió el modelo a Claude Fable 5.2 («Es importante hacerlo con Fable 5.2») y todo
el diseño —elección de cada pieza, pines, esquema, banco de pruebas, placa y ruteo— se hizo con ese modelo.

## 3 · El pedido en una frase (para mostrar en pantalla)

> Diseña un satélite de voz chico: ESP32-S3, micrófono digital I²S, amplificador con parlante,
> LED de estado y USB-C para alimentarlo y programarlo.

## Nota para el guion

La lista de componentes la propuso el modelo y Martín la eligió. La frase «sabía qué componentes
quería usar» es fiel si se entiende así: el tipo de componentes estaba decidido antes de diseñar;
las piezas exactas (por ejemplo, el regulador AP2112K o el amplificador MAX98357A) las eligió el modelo.
