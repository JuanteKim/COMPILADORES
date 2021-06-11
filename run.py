import calc

while True:
	text = input('calc > ')
	result, error = calc.run('<stdin>', text)

	if error: print(error.as_string())
	elif result: print(result)
