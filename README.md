# Eviction Scraping Bot (Neighborhood Preservation, Inc.)
____
The U.S. Department of Treasury granted $28.2M to the City of Memphis and Shelby County to administer [Emergency Rental Assistance (ERA)](https://www.memphistn.gov/news/memphis-and-shelby-county-emergency-rent-and-utility-assistance-program-frequently-asked-questions/) program. With thousands of applicants, it is impossible to manually check every single court date for every case. Therefore, in order to help attorneys appear on behalf of eviction defendants in an organized and consistent way, Innovate Memphis and Neighborhood Preservation, Inc. commissioned this application to scrape, transform, upload, and link data to the intake form responses of those applying for relief. 

Triggered by a recurring Cloudwatch alarm (multiple times per week), a Lambda function initiates the application by pulling the comprehensive list of eviction court case numbers from a Google Sheet maintained by Innovate Memphis and pushing the 30k+ case numbers into an AWS SQS queue. For each case number in the queue, the same Lambda function scrapes the court dates and disposition information from the website, transforms that data into the client requested format, and uploads that into the same Google Sheet. That scrape information is then linked to NPI's intake sheet. This infrastructure is implemented in terraform, located in the `tf/` directory. 

___
Deployment Workflow:
* `$ make clean`: Cleans dependencies -- both python and Chrome/chromedriver -- files (`package/`), zipped AWS Lambda layers (`dist/`), zipped AWS Lambda layers in Terraform dir (`tf/dist/`), and the homemade temporary directory (`temp/`)
* `$ make build`: Downloads dependencies and zips into AWS Lambda layers
* `$ make test`: Runs a test scrape on an example case number (requires Chrome and chromedriver installed in default locations on local machine)
* `$ make deploy`: Applies Terraform code (which requires manual y/n approval from user to officially deploy) which pushes all new code and dependencies into AWS for implementation.

AWS/TF/GCP Configuration:
* Concurrency: Can be run in parallel for scraping X cases at a time in AWS Console or by changing `concurrency` in `tf/lambda.tf`.
* Environmental Variables: Must have the `SPREADSHEET_ID` (which can be found in link to spreadsheet) and `LAMBDA_ENV`=True which tells code that it is running in production and configures paths to Chrome and chromedriver correspondingly.
* Terraform is deployed through the remote backend which stores state (logged at terraform.io) in the just-city organization and builds in Terraform Cloud's run environment. Also includes Terraform-specific environmental variables outlined in `tf/vars.tf`.
* In order to write to the ERA Intake Google Sheet, must have `google_secret.json` service account credentials configured and stored in your local repository -- which is then collected, zipped, and deployed with the Lambda function layer.
