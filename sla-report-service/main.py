import json
import tempfile
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import uuid
import os

# Импорт вашего существующего кода
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

app = FastAPI(
    title="SLA Report Generator API",
    description="API для генерации отчетов SLA в формате PDF",
    version="1.0.0"
)


# Модели Pydantic для валидации данных
class FailureDataPoint(BaseModel):
    timestamp: str
    value: int


class ResponseTimeDataPoint(BaseModel):
    timestamp: str
    value: int


class FailuresByTypes(BaseModel):
    critical: int
    warning: int
    resolved: int


class Metrics(BaseModel):
    uptime: float
    avgResponseTime: int
    incidents: int
    mttr: int
    slaCompliance: float


class SLAReportRequest(BaseModel):
    resourceId: str
    resourceName: str
    url: str
    metrics: Metrics
    stats: Dict[str, Any]


class SLAReportGenerator:
    def __init__(self, data: Dict[str, Any]):
        """
        Инициализация генератора отчетов

        Args:
            data (dict): Данные для отчета в формате JSON
        """
        self.data = data
        self.styles = getSampleStyleSheet()
        self.story = []

        # Регистрируем шрифт с поддержкой кириллицы из файла в папке проекта
        self._register_cyrillic_font()

        # Настройка стилей с кириллическими шрифтами
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName='DejaVuSans',
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName='DejaVuSans',
            fontSize=16,
            spaceAfter=12,
            spaceBefore=12
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            spaceAfter=6
        )

    def _register_cyrillic_font(self):
        """Регистрация шрифта DejaVuSans с поддержкой кириллицы"""
        try:
            # Файл шрифта должен лежать в той же папке, где скрипт (папка проекта)
            font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        except Exception as e:
            print(f"Ошибка регистрации шрифта: {e}")

    def _create_failures_chart(self):
        failures = self.data['stats']['failuresCount']
        timestamps = [datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')) for item in failures]
        values = [item['value'] for item in failures]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timestamps, values, marker='o', linestyle='-', color='#43464B', linewidth=2)

        for i, value in enumerate(values):
            if value > 2:
                color = '#DC2626'  # красный
            elif value > 0:
                color = '#EAB308'  # желтый
            else:
                color = '#16A34A'  # зеленый
            ax.plot(timestamps[i], values[i], 'o', color=color, markersize=8)

        ax.set_title('График сбоев', fontsize=14, pad=20)
        ax.set_ylabel('Количество сбоев')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()

        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close()

        return temp_file.name

    def _create_response_time_chart(self):
        response_times = self.data['stats']['responseTime']
        timestamps = [datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00')) for item in response_times]
        values = [item['value'] for item in response_times]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timestamps, values, marker='o', linestyle='-', color='#43464B', linewidth=2)

        ax.set_title('Время ответа', fontsize=14, pad=20)
        ax.set_ylabel('Время ответа (мс)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()

        ax.axhline(y=100, color='#EAB308', linestyle='--', alpha=0.7, label='Предупреждение (100 мс)')
        ax.axhline(y=300, color='#DC2626', linestyle='--', alpha=0.7, label='Критический (300 мс)')
        ax.legend()

        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close()

        return temp_file.name

    def _create_failure_types_chart(self):
        failures_by_types = self.data['stats']['failuresByTypes']
        labels = ['Critical', 'Warning', 'Resolved']
        values = [failures_by_types['critical'], failures_by_types['warning'], failures_by_types['resolved']]
        colors = ['#DC2626', '#EAB308', '#16A34A']

        fig, ax = plt.subplots(figsize=(6, 4))
        wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)

        ax.set_title('Типы ошибок', fontsize=14, pad=20)

        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close()

        return temp_file.name

    def _create_metrics_table(self):
        metrics = self.data['metrics']

        metrics_data = [
            ['Метрика', 'Значение', 'Цель'],
            ['Доступность', f"{metrics['uptime']}%", "99.9%"],
            ['Время отклика', f"{metrics['avgResponseTime']} мс", "< 200 мс"],
            ['Инциденты', str(metrics['incidents']), "Минимум"],
            ['Среднее время восстановления', f"{metrics['mttr']} мин", "< 60 мин"],
            ['Соблюдение SLA', f"{metrics['slaCompliance']}%", "> 99%"]
        ]

        table = Table(metrics_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        return table

    def generate_report(self, output_filename: str):
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        title = Paragraph("SLA ОТЧЕТ ПО РАБОТЕ СЕРВИСА", self.title_style)
        self.story.append(title)

        resource_info = [
            [Paragraph("<b>Ресурс:</b>", self.normal_style), Paragraph(self.data['resourceName'], self.normal_style)],
            [Paragraph("<b>URL:</b>", self.normal_style), Paragraph(self.data['url'], self.normal_style)],
            [Paragraph("<b>ID ресурса:</b>", self.normal_style), Paragraph(self.data['resourceId'], self.normal_style)],
            [Paragraph("<b>Дата отчета:</b>", self.normal_style),
             Paragraph(datetime.now().strftime("%d.%m.%Y"), self.normal_style)]
        ]

        resource_table = Table(resource_info, colWidths=[1.5 * inch, 4 * inch])
        resource_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ]))

        self.story.append(resource_table)
        self.story.append(Spacer(1, 0.25 * inch))

        metrics_heading = Paragraph("Ключевые метрики", self.heading_style)
        self.story.append(metrics_heading)
        self.story.append(self._create_metrics_table())
        self.story.append(Spacer(1, 0.25 * inch))

        failures_heading = Paragraph("График сбоев", self.heading_style)
        self.story.append(failures_heading)
        failures_chart_path = self._create_failures_chart()
        self.story.append(Image(failures_chart_path, width=6 * inch, height=2.5 * inch))
        self.story.append(Spacer(1, 0.25 * inch))

        response_time_heading = Paragraph("Время ответа", self.heading_style)
        self.story.append(response_time_heading)
        response_time_chart_path = self._create_response_time_chart()
        self.story.append(Image(response_time_chart_path, width=6 * inch, height=2.5 * inch))
        self.story.append(Spacer(1, 0.25 * inch))

        failure_types_heading = Paragraph("Типы ошибок", self.heading_style)
        self.story.append(failure_types_heading)
        failure_types_chart_path = self._create_failure_types_chart()
        self.story.append(Image(failure_types_chart_path, width=4 * inch, height=3 * inch))

        doc.build(self.story)

        try:
            os.unlink(failures_chart_path)
            os.unlink(response_time_chart_path)
            os.unlink(failure_types_chart_path)
        except Exception:
            pass

        return output_filename


@app.get("/")
async def root():
    return {"message": "SLA Report Generator API", "version": "1.0.0"}


@app.post("/generate-report")
async def generate_sla_report(report_data: SLAReportRequest):
    """
    Генерация отчета SLA в формате PDF

    Принимает данные отчета и возвращает сгенерированный PDF файл
    """
    try:
        # Конвертируем Pydantic модель в dict
        data_dict = report_data.dict()

        # Создаем временный файл для отчета
        temp_dir = tempfile.gettempdir()
        report_filename = f"sla_report_{uuid.uuid4().hex}.pdf"
        report_path = os.path.join(temp_dir, report_filename)

        # Генерируем отчет
        generator = SLAReportGenerator(data_dict)
        generated_path = generator.generate_report(report_path)

        # Возвращаем файл как ответ
        return FileResponse(
            generated_path,
            media_type="application/pdf",
            filename=f"sla_report_{data_dict['resourceName']}.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации отчета: {str(e)}")


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)