import os
import pandas as pd
import pyzipper
import shutil
from connect import connect_single_query


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
    folder_path = './PDF'  # Replace with the actual path to your folder

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            tvid_list.append(filename[:6])
    return tvid_list


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

        tvid_list = get_tvid()
        if len(tvid_list) == 0:
            if progress_error:
                progress_error('No PDF files in the folder.')
            print('No PDF files in the folder.')
        else:

            tvid_text = ""
            for e, each in enumerate(tvid_list):
                if e == 0:
                    tvid_text += f"'{each}'"
                else:
                    tvid_text += f", '{each}'"

            query = f"SELECT [t_vid], [ms_m_mid] FROM [MDM_PROD].[dbo].[terminal] t LEFT JOIN [MDM_PROD].[dbo].[" \
                    f"merchant_shop] ms ON ms.[ms_id] = t.[t_ms_id] WHERE t_vid IN ({tvid_text})"

            with open("query.txt", "w") as file:
                file.write(query)

            df = connect_single_query(query, passw, user)

            for row in range(df.shape[0]):
                input_file = f'./PDF/{df.iat[row, 0]}.pdf'  # Replace with the file you want to zip
                output_zip = f'./ZIP/{df.iat[row, 0]}_encrypted.zip'  # Replace with the desired output zip filename
                password = f'{df.iat[row, 1]}'  # Replace with the desired password

                if pd.isnull(password):
                    shutil.move(input_file, f'./ERROR/{df.iat[row, 0]}.pdf')
                else:
                    zip_with_password(input_file, output_zip, password)
                    shutil.move(input_file, f'./ARCHIVE/{df.iat[row, 0]}.pdf')

        final_text = 'All the files were zipped succesfully: '
        for t, tvid in enumerate(tvid_list):
            if t == len(tvid_list) - 1:
                final_text += f'{tvid}.pdf. You can find encrypted files in ZIP folder.'
            else:
                final_text += f'{tvid}.pdf, '
        if len(tvid_list) > 0:
            progress_error(final_text)
    except Exception as e:
        if progress_error:
            progress_error(e)


if __name__ == '__main__':
    try:
        generate()
    except ConnectionError as e:
        print('Error', e)

    input('Press any key to exit...')
