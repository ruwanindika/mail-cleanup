# Package the Lambda layer 
data "archive_file" "lambda_layer_zip" {
  type        = "zip"
  source_dir = "${path.module}/../dependencies/python"
  output_path = "${path.module}/../dependencies/python.zip"
}

# lambda layer 
resource "aws_lambda_layer_version" "gmail_api_lib" {
  filename   = data.archive_file.lambda_layer_zip.output_path
  layer_name = "gmail_api_lib"
  source_code_hash = data.archive_file.lambda_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.13"]
}