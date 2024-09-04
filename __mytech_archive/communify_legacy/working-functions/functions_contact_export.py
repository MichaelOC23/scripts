import json
import subprocess

def get_contacts_from_applescript():
    script = """
   tell application "Contacts"
    set allContacts to every person
    set output to ""
    repeat with aContact in allContacts
        set contactInfo to (get first name of aContact) & ", " & (get last name of aContact) & ", " & (get organization of aContact) & ", " & (get job title of aContact) & ", "

        -- Handle emails
        set emailList to emails of aContact
        if emailList is not missing value then
            repeat with anEmail in emailList
                set contactInfo to contactInfo & (value of anEmail) & "; "
            end repeat
        end if
        set contactInfo to contactInfo & ", "

        -- Handle phones
        set phoneList to phones of aContact
        if phoneList is not missing value then
            repeat with aPhone in phoneList
                set contactInfo to contactInfo & (value of aPhone) & "; "
            end repeat
        end if
        set contactInfo to contactInfo & ", "

        -- Handle addresses
        set addressList to addresses of aContact
        if addressList is not missing value then
            repeat with anAddress in addressList
                set contactInfo to contactInfo & (street of anAddress) & " " & (city of anAddress) & " " & (zip of anAddress) & "; "
            end repeat
        end if
        set contactInfo to contactInfo & "\n"

        set output to output & contactInfo
    end repeat
end tell


    """
    process = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return process.stdout

def convert_to_json(contact_data):
    contacts = []
    for line in contact_data.strip().split("\n"):
        parts = line.split(", ")
        if len(parts) >= 7:
            first_name, last_name, organization, job_title, emails, phones, addresses = parts[:7]
            contact_info = {
                "first_name": first_name,
                "last_name": last_name,
                "organization": organization,
                "job_title": job_title,
                "emails": emails.split("; "),  # Assuming emails are separated by "; "
                "phones": phones.split("; "),  # Assuming phones are separated by "; "
                "addresses": addresses.split("; ")  # Assuming addresses are separated by "; "
            }
        else:
            # Handle cases where some fields might be missing
            contact_info = {"info": "Incomplete data for this contact"}
        
        contacts.append(contact_info)

    return json.dumps(contacts, indent=4)

def main():
    contact_data = get_contacts_from_applescript()
    contacts_json = convert_to_json(contact_data)
    with open("contacts.json", "w") as file:
        file.write(contacts_json)

if __name__ == "__main__":
    main()