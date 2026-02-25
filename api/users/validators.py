from django.core.exceptions import ValidationError

def validate_cpf(value):
        # Remover pontuação
        cpf = ''.join(char for char in value if char.isdigit())        
        # Validar tamanho
        if len(cpf) != 11:
            raise ValidationError("CPF deve conter 11 dígitos.")
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            raise ValidationError("CPF inválido (todos dígitos iguais).")
        
        # Função para calcular dígitos verificadores
        def calculate_digit(cpf_slice, factor):
            total = 0
            for digit in cpf_slice:
                total += int(digit) * factor
                factor -= 1
            remainder = total % 11
            return '0' if remainder < 2 else str(11 - remainder)
        
        # Calcular os dois dígitos verificadores
        first_digit = calculate_digit(cpf[:9], 10)
        second_digit = calculate_digit(cpf[:9] + first_digit, 11)
        print(f"Dígitos calculados: {first_digit}{second_digit}")
        
        # Validar CPF final
        if cpf[-2:] != first_digit + second_digit:
            raise ValidationError("CPF inválido (dígitos verificadores incorretos).")

    
def validate_telefone(value):
    try:
        # Remover qualquer caractere que não seja dígito
        telefone = ''.join(char for char in value if char.isdigit())
        print(f"Telefone limpo: {telefone}")

        # Validar tamanho (aceita 10 ou 11 dígitos — com ou sem DDD + 9)
        if len(telefone) not in [10, 11]:
            raise ValidationError("Telefone deve conter 10 ou 11 dígitos (incluindo DDD).")

        # DDD válido (01–99, mas vamos excluir DDDs inválidos comuns como 00)
        if telefone[:2] in ['00']:
            raise ValidationError("DDD inválido.")

        # Se tiver 11 dígitos, o terceiro deve ser 9 (telefone celular)
        if len(telefone) == 11 and telefone[2] != '9':
            raise ValidationError("Telefone celular deve começar com 9 após o DDD.")

        # Se tiver 10 dígitos, o terceiro não pode ser 0 nem 1 (telefone fixo)
        if len(telefone) == 10 and telefone[2] in ['0', '1']:
            raise ValidationError("Telefone fixo inválido.")

        # Evitar números repetidos (tipo 1111111111)
        if telefone == telefone[0] * len(telefone):
            raise ValidationError("Telefone inválido (todos os dígitos iguais).")

        print("Telefone validado com sucesso!")

    except ValidationError as e:
        print(f"Erro de validação: {e}")
        raise
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise ValidationError("Erro ao validar telefone.")