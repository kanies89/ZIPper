import os
import pandas as pd
import pyzipper
import shutil
from connect import connect_single_query
import pyodbc


def zip_with_password(input_file, output_zip, password):
    with pyzipper.AESZipFile(output_zip, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode())
        zf.write(input_file)


def create_folder_structure(address):
    # Check if the folder structure exists
    if not os.path.exists(address):
        # Create the folder structure
        os.makedirs(address)
        print("Folder structure created successfully.")
    else:
        print("Folder structure already exists.")


def get_tvid():
    tvid_list = []
    file_list = []
    folder_path = './PDF'  # Replace with the actual path to your folder

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            tvid_list.append(filename[:6])
            file_list.append(filename)
    print(tvid_list)
    print(file_list)
    return tvid_list, file_list


def encrypt(df, tvid_list, file_list, progress_error=None):
    tvid_list_not_found = []
    tvid_list_found = []

    list_of_tvids_in_database = df['t_vid'].to_list()

    for ind in range(len(tvid_list)):
        print(ind)
        print(file_list[ind])

        input_file = f'./PDF/{file_list[ind]}'  # Replace with the file you want to zip

        # If TVID not in database
        if tvid_list[ind] in list_of_tvids_in_database:
            print('On the list')
            output_zip = f'./ZIP/{tvid_list[ind]}_encrypted.zip'  # Replace with the desired output zip filename
            password = f'{df["ms_m_mid"][ind]}'  # Replace with the desired password

            if pd.isnull(password):
                shutil.move(input_file, f'./ERROR/{tvid_list[ind]}_mid_is_null.pdf')
                tvid_list_not_found.append(tvid_list[ind])
            else:
                zip_with_password(input_file, output_zip, password)
                shutil.move(input_file, f'./ARCHIVE/{tvid_list[ind]}.pdf')
                tvid_list_found.append(tvid_list[ind])

        else:
            shutil.move(input_file, f'./ERROR/{tvid_list[ind]}_not_found_in_database.pdf')
            tvid_list_not_found.append(tvid_list[ind])

    final_text = 'All the files were zipped succesfully: '
    if len(tvid_list_found) > 0:
        for t, tvid in enumerate(tvid_list_found):
            if t == len(tvid_list) - 1:
                final_text += f'{tvid}.pdf. You can find encrypted files in ZIP folder.'
            else:
                final_text += f'{tvid}.pdf, '

        progress_error(final_text)

    final_text = 'Those files were moved to ERROR folder: '
    if len(tvid_list_not_found) > 0:
        for t, tvid in enumerate(tvid_list_not_found):
            if t == len(tvid_list) - 1:
                final_text += f'{tvid}.pdf.'
            else:
                final_text += f'{tvid}.pdf, '

        progress_error(final_text)


def generate(passw, user, progress_error=None):
    try:
        # Check if address folder exist. If not then create.
        address = './PDF'
        if not os.path.exists(address):
            create_folder_structure(address)

        # Check if address folder exist. If not then create.
        address = './ZIP'
        if not os.path.exists(address):
            create_folder_structure(address)

        # Check if address folder exist. If not then create.
        address = './ARCHIVE'
        if not os.path.exists(address):
            create_folder_structure(address)

        # Check if address folder exist. If not then create.
        address = './ERROR'
        if not os.path.exists(address):
            create_folder_structure(address)

        prepare_data = get_tvid()

        tvid_list = prepare_data[0]
        file_list = prepare_data[1]

        if len(tvid_list) == 0:
            if progress_error:
                progress_error('No PDF files in the folder.')
            print('No PDF files in the folder.')
        else:
            tvid_text = ""

            for i, each in enumerate(tvid_list):
                if i == 0:
                    tvid_text += f"'{each}'"
                else:
                    tvid_text += f", '{each}'"

            query = f"SELECT [t_vid], [ms_m_mid] FROM [MDM_PROD].[dbo].[terminal] t LEFT JOIN [MDM_PROD].[dbo].[" \
                    f"merchant_shop] ms ON ms.[ms_id] = t.[t_ms_id] WHERE t_vid IN ({tvid_text})"

            with open("query.txt", "w") as file:
                file.write(query)

            df = connect_single_query(query, passw, user)

            encrypt(df, tvid_list, file_list, progress_error)

    except (Exception, pyodbc.InterfaceError, ConnectionError) as e:
        if progress_error:
            progress_error(str(e))


if __name__ == '__main__':
    try:
        generate()
    except ConnectionError as e:
        print('Error', e)

    input('Press any key to exit...')
