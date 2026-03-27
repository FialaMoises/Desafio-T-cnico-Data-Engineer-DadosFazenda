import re


class CPFAnonymizer:
    @staticmethod
    def anonymize(cpf: str) -> str:
        digits = re.sub(r'\D', '', cpf)

        if len(digits) == 10:
            digits = '0' + digits

        if len(digits) != 11:
            return "***.***.***-**"

        return f"***.***.*{digits[7:9]}-{digits[9:11]}"
