# (1)
FROM python:3.9

# (2)
WORKDIR /SIMYOU_LLM_SERVICE

# (3)
COPY ./requirements.txt /SIMYOU_LLM_SERVICE/requirements.txt

# (4)
RUN pip install --no-cache-dir --upgrade -r /SIMYOU_LLM_SERVICE/requirements.txt

# (5)
COPY ./app /SIMYOU_LLM_SERVICE/app

# (6)
EXPOSE 8000

# (7)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]