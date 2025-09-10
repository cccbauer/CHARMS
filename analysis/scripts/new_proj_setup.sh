#!bin/bash

#####################################################################################
# Use this script to set up the structure of the folders for a new project
#####################################################################################

# how to run:
# $sh new_proj_setup.sh nameOfNewMainProject


######################
proj_name=$1

# check that user gave projectname
if [ -z "$proj_name" ]; then
    echo "WARNING you need to pass the name of the folder to be created, eg $sh new_proj_setup.sh NameOfTheMainProject"
    exit
fi

main_dir=/vast/swglab/data/${proj_name}

#check that projectname (and associated folder) dont exist already
if [[ ! -e $main_dir ]]; then
    mkdir $main_dir
elif [[ -e $main_dir ]]; then
    echo "ERROR ${main_dir} already exists. Make sure you are not duplicating a project or the name"
    exit
fi

# create folder structure
# protocols
mkdir -p ${main_dir}/protocols
touch ${main_dir}/protocols/README.txt
echo "add here info about versions, design, changes to the original protocol etc." >> ${main_dir}/protocols/README.txt


# sourcedata
mkdir -p ${main_dir}/sourcedata/dicoms
mkdir -p ${main_dir}/sourcedata/task_outputs
mkdir -p ${main_dir}/sourcedata/behavioral_data


# other folders
mkdir -p ${main_dir}/analysis
mkdir -p ${main_dir}/rawdata
mkdir -p ${main_dir}/working_files
mkdir -p ${main_dir}/derivatives
mkdir -p ${main_dir}/quality_control
mkdir -p ${main_dir}/archive
mkdir -p ${main_dir}/scripts
touch ${main_dir}/README.txt
echo "add here Google Drive folder with info (if any), info about the main project, funding information, start and end date.." >> ${main_dir}/README.txt



echo "ALL GOOD, folder structure created here: ${main_dir}"
echo "Please look at this Google Drive document to know how to use the folders and where files should be stored: https://docs.google.com/document/d/10pm66OMqXpQjMnGwpBLFa-bZ6_mfseoyEvjpzHWVrv8/edit"
