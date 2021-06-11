Para correr el programa
python3 run.py

Para proyecto final de esta materia crearemos un pequeño compilador, para un lenguaje con las siguientes funcionalidades:

Aritméticas:
Suma: 1 + 1
Resta: 1 - 1
Multiplicación:  1 * 5
División: 5 / 1
Exponenciación: 5 ^ 2

Comparación:
==: 1 == 1
!=: 1 != 1
>: 1 > 3
<: 1 < 3
>=: 1 >= 3
<=: 1 <= 3

Booleanas
and: 1 == 1 AND 1 < 3
or: 1 ==  1 OR 1 < 3

Operaciones de bloques:
( ): (1 + 3) * (3 * 8)
{}:

Flujos de control existentes, deberan seguir una estructura similar al lenguaje C, por simplicidad todo deberán llevar llaves:
if-expr			: KEYWORD:IF expr KEYWORD:THEN expr
							(KEYWORD:ELIF expr KEYWORD:THEN expr)*
							(KEYWORD:ELSE expr)?

for-expr		: KEYWORD:FOR IDENTIFIER EQ expr KEYWORD:TO expr 
							(KEYWORD:STEP expr)? KEYWORD:THEN expr

while-expr	: KEYWORD:WHILE expr KEYWORD:THEN expr