FROM public.ecr.aws/lambda/python:3.11

RUN yum update -y libxml2

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["app.main.lambda_handler"] 