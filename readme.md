# Callensights Setup Guide

This guide provides comprehensive instructions for setting up and running Callensights on your local machine.

## Prerequisites

Ensure you have the following prerequisites installed on your system:

- Python 3.6 or higher
- MySQL Server

## Getting Started

Follow these steps to quickly get the application up and running:

1. **Clone the Repository**

   Clone the Callensights repository using the following command:

   ```bash
   git clone <repository_url>
   ```

2. **Install Dependencies**

   Navigate to the project directory and install the required Python packages using pip:

   ```bash
   cd <project_directory>
   pip install -r requirements.txt
   ```

3. **Run the Application**

   Start the FastAPI server with the following command:

   ```bash
   uvicorn application:application --reload
   ```

## Setting Up MySQL Server (Unfinished Docs)

If MySQL Server is not installed, follow these steps to install and run it on MacOS using [Homebrew](https://formulae.brew.sh/formula/mysql):

1. **Install MySQL Server**

   ```bash
   brew install mysql
   ```

2. **Start MySQL Server**

   ```bash
   mysql.server start
   ```

3. **Stop MySQL Server**

   ```bash
   mysql.server stop
   ```

   Note: For some users, starting MySQL as a service may be preferred using `brew services start mysql`, but exercise caution.

## Installing a MySQL GUI Tool

Choose from a variety of GUI tools for MySQL such as [MySQLWorkBench](https://dev.mysql.com/downloads/workbench/), [Table Plus](https://tableplus.com/) (`Recommended`), or [DBeaver](https://dbeaver.io/download/) (`Recommended`).

## Defining Data Definition Language (DDL) Scripts

Access the complete schema in [ddl.sql](./app/db_scripts/ddl.sql) and execute the scripts using your chosen MySQL GUI tool.

## Migrating Users [Important]

Insert users into the User table, as the webhook is deployed to production servers while development occurs on the dev server. Obtain your Clerk User ID from the [Clerk Dashboard](https://dashboard.clerk.com) and insert the necessary users for the application. Note that inserting all users is not required.
