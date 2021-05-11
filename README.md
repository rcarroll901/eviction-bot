# Eviction Scraping Bot (Neighborhood Preservation, Inc.)
____
The U.S. Department of Treasury granted $28.2M to the City of Memphis and Shelby County to administer [Emergency Rental Assistance (ERA)](https://www.memphistn.gov/news/memphis-and-shelby-county-emergency-rent-and-utility-assistance-program-frequently-asked-questions/) program. With thousands of applicants, it is impossible to manually check every single court date for every case. Therefore, in order to help attorneys appear on behalf of eviction defendants in an organized and consistent way, Innovate Memphis and Neighborhood Preservation, Inc. commissioned this application to scrape, transform, upload, and link data to the intake form responses of those applying for relief. 

Triggered by a recurring Cloudwatch alarm (multiple times per week), a Lambda function initiates the application by pulling the comprehensive list of eviction court case numbers from a Airtable maintained by NPI and US Digital Response and pushing the ~1k case numbers into an AWS SQS queue. For each case number in the queue, the same Lambda function scrapes the (previous and future) court dates and disposition information from the website, transforms that data into the client requested format, and uploads that into the same Airtable base. This AWS infrastructure is implemented in terraform, located in the `tf/` directory. 

___

Development Setup:

1. Obtain and save the following variables in a `.env` file:
    ```
    CASE_LINK="url_to_api_endpoint"
    SQS_URL="url_to_AWS_SQS_endpoint"
    AT_API_KEY="api_access_key_obtained_from_airtable"
    AT_BASE_KEY="base_key_obtained_from_airtable"
    AT_TABLE_NAME="table_name_which_contains_eviction_cases"
    ```
2. If `pipenv` is not installed on your machine, run `$ pip3 install pipenv`
3. Run `$ pipenv sync` while working directory is in repository root (with `Pipfile.lock`)
    * If you prefer developing in jupyter notebooks, run `$ pipenv sync -d`
4. Run `$ pipenv shell` to enter virtual environment

Deployment Workflow:
* `$ make clean`: Cleans Python dependencies files (`package/`), zipped AWS Lambda layers (`dist/`), zipped AWS Lambda layers in Terraform dir (`tf/dist/`), and the homemade temporary directory (`temp/`)
* `$ make build`: Downloads dependencies and zips into AWS Lambda layers
* `$ make test-scrape`: Runs a test scrape on an example case number and uploads to Airtable
* `$ make test-flow`: Runs a scrape and then uploads to Airtable
* `$ make deploy`: Applies Terraform code (which requires manual y/n approval from user to officially deploy) which pushes all new code and dependencies into AWS for implementation.
* `$ make test-lambda`: Uploads a single case to SQS queue and fires lambda function. Results can be checked in AWS Cloudwatch

AWS/TF/AT Configuration:
* List of cases are assumed to be in "Eviction Case Number" column in Airtable. Names of scraped data columns can be found in `evict_tools/scrape.py` within `EvictionScraper` methods.
* Concurrency: Can be run in parallel for scraping X cases at a time in AWS Console or by changing `concurrency` in `tf/lambda.tf` (or in the console). Site seems to not handle more than concurrency = 3.
* Terraform is deployed through the remote backend which stores state (logged at terraform.io) in the just-city organization and builds in Terraform Cloud's run environment. Also includes Terraform-specific environmental variables outlined in `tf/vars.tf`.
