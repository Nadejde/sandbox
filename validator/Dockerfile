FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt *.py ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=loggers *.py loggers/

CMD ["python", "agent_sandbox.py"]
