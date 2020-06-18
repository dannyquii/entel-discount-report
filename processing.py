from models.ProcessDTO import ProcessDTO
import re
import string

gloss_column = 3
discount_column = 2
amount_column = 5

required_fields = {gloss_column, discount_column, amount_column}

# Fields
# 0 CUENTA
# 1 TIPO
# 2 MONTO
# 3 GLOSA
# 4 TIPO2
# 5 CANTIDAD
# 6 USUARIO
# 7 FECHA
# 8 TIPOIMPUESTO
# 9 TIPO3
# 10 TIPO4
# 11 CLASE
# 12 TIPO5
# 13 TIPO6
# 14 CODIGO
# 15 CONTRATO
# 16 CODIGOSECUNDARIO
# 17 CUENTA
# 18 SERVICIO
# 19 OPS
# 20 OTS
# 21 ORE
# 22 ORR


def process_line(process_dto):
    """
    Función encargada de procesar una linea.
    :param process_dto:
    :return:
    """

    if not process_dto.current_line:
        return

    fields = process_dto.current_line.split(";")
    if ProcessDTO.total_columns != len(fields):
        process_dto.discard_current_line()
        return

    repaired = False

    for i in range(len(fields)):
        field = fields[i]

        if i == gloss_column:
            continue

        if re.search(r'\s', field):
            field = field.translate({ord(c): None for c in string.whitespace})
            if not field and i in required_fields:
                process_dto.discard_current_line()
                return
            repaired = True

            fields[i] = field

        elif not field and i in required_fields:
            process_dto.discard_current_line()
            return

    try:
        process_dto.update_financial_stat(
            fields[gloss_column],
            fields[amount_column],
            fields[discount_column]
        )
    except TypeError:
        process_dto.discard_current_line()
        return

    if repaired:
        process_dto.add_repaired_line(";".join(str(x) for x in fields))

    process_dto.add_ok()


def process_partition(process_dto, index_range):
    """
    Procesa una partición de una lista de lineas del archivo de entrada.
    :param process_dto:
    :param index_range:
    :return:
    """
    for i in index_range:
        process_dto.set_current_line(i)
        process_line(process_dto)
