import math
import logging
import threading
import time
import os
from os import listdir
from os.path import isfile
from datetime import date
from processing import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def make_discard_file(filename, merge_process_dto):
    """
    creación de archivo con las lineas descartadas
    :return:
    """

    filename_prefix = os.path.splitext(os.path.basename(filename))[0]
    file_path = os.path.dirname(filename)

    report_path = file_path + os.path.sep + "reports"
    if not os.path.isdir(report_path):
        os.mkdir(report_path)

    with open(report_path + os.path.sep + filename_prefix + "-discarded-records.txt", "w") as file:
        file.write("\n".join(merge_process_dto.execution_stat.discarded_lines))
    pass


def make_financial_report(filename, merge_process_dto):
    """
    creación de archivo con las lineas procesadas
    :return:
    """
    file_content =\
        [
            "{}{}\n{:>59}\nFecha: {}\n{}{}\n\n{:68}{:>12}{:>20}\n"
            .format(
                "--------------------------------------------------",
                "--------------------------------------------------",
                "RESUMEN DE DESCUENTOS",
                date.today(),
                "--------------------------------------------------",
                "--------------------------------------------------",
                "Tipo de descuento",
                "Cantidad",
                "Monto"
            )
        ]

    keys = list(merge_process_dto.financial_stat.keys())
    keys.sort()

    sum_item_discount = 0
    for key in keys:
        item = merge_process_dto.financial_stat.get(key)
        file_content.append("{:68}{:>12}{:>20}".format(key, item.count, item.discount))
        sum_item_discount += item.discount

    file_content.append(
        "\n{}{}\n{:>79}: {:>19}".format(
            "--------------------------------------------------",
            "--------------------------------------------------",
            "Total descuentos",
            sum_item_discount
        )
    )

    filename_prefix = os.path.splitext(os.path.basename(filename))[0]
    file_path = os.path.dirname(filename)

    report_path = file_path + os.path.sep + "reports"
    if not os.path.isdir(report_path):
        os.mkdir(report_path)

    with open(report_path + os.path.sep + filename_prefix + "-financial-report.txt", "w") as file:
        file.write("\n".join(file_content))


def modify_file(filename, merge_process_dto):
    with open(filename, 'r') as file:
        f_content = file.readlines()

    with open(filename, 'w') as file:
        for repaired_line in merge_process_dto.execution_stat.repaired_lines:
            f_content[repaired_line.line_id] = repaired_line.content + "\n"

        file.writelines(f_content)


def ls1(path):
    """
    :param path: Directorio raiz que se desea analizar
    :return: lista con los nombres de archivos encontrados en el directorio.
    """
    return [obj for obj in listdir(path) if isfile(path + obj)]


def make_execution_report(filename, merge_process_dto):
    """
        creación de archivo con reporte de ejecución
    """
    file_content = list()

    file_content.append(
        "{}{}\n{:>59}\n{}{}\n".format(
            "--------------------------------------------------",
            "--------------------------------------------------",
            "REPORTE DE EJECUCIÓN",
            "--------------------------------------------------",
            "--------------------------------------------------"
        )
    )

    basename = os.path.basename(filename)

    file_content.append(
        ("{:32}:{:>40}\n".join(["", "", "", "", "", "", "", ""])).format(
            "Nombre de archivo",
            basename,
            "Fecha",
            str(date.today()),
            "Total procesados",
            merge_process_dto.execution_stat.get_total_processed(),
            "Correctos",
            merge_process_dto.execution_stat.processed,
            "Reparados",
            len(merge_process_dto.execution_stat.repaired_lines),
            "Descartados",
            len(merge_process_dto.execution_stat.discarded_lines),
            "Tiempo de ejecución en segundos",
            merge_process_dto.execution_stat.elapsed_time
        )
    )

    filename_prefix = os.path.splitext(basename)[0]
    file_path = os.path.dirname(filename)

    report_path = file_path + os.path.sep + "reports"
    if not os.path.isdir(report_path):
        os.mkdir(report_path)

    with open(report_path + os.path.sep + filename_prefix + "-execution-report.txt", "w") as file:
        file.write("\n".join(file_content))


def make_report(filename):
    """
    Procesa el archivo de entrada y construye reporte financiero y de ejecución.
    :param filename: rRuta del archivo.
    :return:
    """
    logger.info("Inicia procesamiento de archivo")
    logger.debug("Abriendo archivo:\n%s", filename)

    start_time = time.time()

    with open(filename, 'r') as file:
        data = file.read()
        ProcessDTO.lines = data.split("\n")
        total_lines = len(ProcessDTO.lines) - 1
        if not re.search(r'GLOSA', ProcessDTO.lines[0]):
            logger.error("Header 'GLOSA' no encontrada.")
            return

        logger.debug("definiendo particionado para procesado concurrente...")

        if total_lines < ProcessDTO.total_threads:
            ProcessDTO.total_threads = total_lines

        partition_size = math.floor(total_lines / ProcessDTO.total_threads)
        last_partition_size = total_lines - (ProcessDTO.total_threads - 1) * partition_size

        logger.debug(
            "total lines         = %d\npartition size      = %d\nlast partition size = %d",
            total_lines,
            partition_size,
            last_partition_size
        )

        ProcessDTO.total_columns = len(ProcessDTO.lines[0].split(";"))
        threads_range = range(ProcessDTO.total_threads)
        max_index = max(threads_range)
        threads = []
        process_list_dto = []
        current_partition_size = partition_size

        if partition_size != 0:
            logger.debug("Iniciando procesamiento concurrente")
            for i in threads_range:
                if i == max_index:
                    current_partition_size = last_partition_size

                process_list_dto.append(ProcessDTO())
                threads.append(
                    threading.Thread(
                        target=process_partition,
                        args=(
                            process_list_dto[i],
                            range(
                                1 + i * partition_size,
                                1 + i * partition_size + current_partition_size
                            )
                        )
                    )
                )
                threads[i].start()

            for i in threads_range:
                threads[i].join()

            logger.debug("Procesamiento concurrente finalizado")
        else:
            logger.debug("Se procesa en thread principal")
            process_list_dto.append(ProcessDTO())
            process_partition(process_list_dto[0], range(1, 1 + last_partition_size))
            logger.debug("Proceso en hilo principal finalizado")

    logger.info("Generando reportes")

    merge_process_dto = ProcessDTO()

    logger.debug("Merging data")
    for process_item_dto in process_list_dto:
        merge_process_dto.merge_stats(process_item_dto)

    merge_process_dto.set_elapsed_time((time.time() - start_time))
    make_financial_report(filename, merge_process_dto)
    make_discard_file(filename, merge_process_dto)
    make_execution_report(filename, merge_process_dto)
    modify_file(filename, merge_process_dto)

    logger.info("Reportes generados.")


def make_reports(work_path):
    work_path = work_path.replace("/", os.path.sep) + os.path.sep
    files = ls1(work_path)
    ProcessDTO.total_threads = 8

    for base_filename in files:
        make_report(work_path + os.path.sep + base_filename)
