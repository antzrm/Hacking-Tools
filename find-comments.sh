#!/bin/bash

# Colours
greenColour="\e[0;32m\033[1m"
endColour="\033[0m\e[0m"
redColour="\e[0;31m\033[1m"
blueColour="\e[0;34m\033[1m"
yellowColour="\e[0;33m\033[1m"
purpleColour="\e[0;35m\033[1m"
turquoiseColour="\e[0;36m\033[1m"
grayColour="\e[0;37m\033[1m"

function ctrl_c(){
        echo -e "Exiting..."
        tput cnorm; exit 1
}

#Ctrl+C
trap ctrl_c SIGINT

function helpPanel(){
        echo -e "\n Usage: $0 -j JSON-file -f file -u URL\n"
        echo -e "\t -f file with full URLs and paths"
        echo -e "\t -u URL with format http(s)://URL/path where path is directory/file"
        echo -e "\t -j ffuf JSON file"
        tput cnorm; exit 1
}

declare -i parameter_counter=0

tput civis

while getopts "u:j:f:h" arg; do
        case $arg in
                u) url=$OPTARG && let parameter_counter+=1;;
                j) json=$OPTARG && let parameter_counter+=1;;
                f) file=$OPTARG && let parameter_counter+=1;;
                h) helpPanel
        esac
done

function directoryListingCheck(){
        file=$1

        rm URLs 2>/dev/null
        if [ "$(echo $file | grep '.json$')" ]; then #if json file
                echo -e "[+] Extracting URLs from JSON file..."
                cat $file | jq -r '.results |  .[] | .url' > URLs
        else #normal file with URLs and paths
                cp $file URLs
        fi
        echo -e "[+] Visiting existing URLs to find directory listing..."
        for path in $(cat URLs); do
                if [ "$(echo $path | grep '/$')" ] && [ "$(curl -s $path | grep 'Index of /')" ]; then #valid directory with / at the end, and with directory listing enabled
                        #Get all files from directory listing recursively
                        wget -d -r -np -N --spider -e robots=off --no-check-certificate $path 2>&1 | grep " -> " | grep -Ev "\/\?C=" | sed "s/.* -> //" | grep -E "http://|https://" >> URLs
                elif [ ! "$(echo $path | awk '{print $NF}' FS='/' | grep -woP '.*\..{2,4}')" ]; then #it is not a simple file
                        path+="/"
                        if [ "$(curl -s $path | grep 'Index of /')" ]; then #if directory listing enabled
                                wget -d -r -np -N --spider -e robots=off --no-check-certificate $path 2>&1 | grep " -> " | grep -Ev "\/\?C=" | sed "s/.* -> //" | grep -E "http://|https://" >> URLs
                        fi
                fi
        done
        echo -e "[+] Directory Listing Check finished, sorting all unique URLs..."
        sed -ni '/^http/p' URLs #only leave real URLs that start with http
        sort -u URLs -o URLs #remove dupes
}

function checkLinks(){
        rm links 2>/dev/null
        touch links
        echo -e "[+] Checking if any URL has additional links on its source code..."
        for path in $(cat URLs); do
                curl -s $path | grep -oP '<a href="(.*)"' | cut -d '"' -f 2 >> links
        done
        echo -e "[+] Links Check finished, sorting all unique links..."
        sort -u links -o links
        grep -E 'http://|https://' links >> URLs #in case new URLs with absolute paths
        #Get rid of useless URLs
        sed -ni '/google/!p' URLs
        sed -ni '/youtube/!p' URLs
        sort -u URLs -o URLs

        if [ "$(wc -l links | cut -d ' ' -f 1)" -ne 0 ]; then
                echo -e "\n[+] Check possible new links on ${redColour}links${endColour} file\n"
        fi
}

function findComments(){
        rm comments 2>/dev/null
        echo -e "\n${yellowColour} [+] Fetching comments...${endColour}"
        for path in $(cat URLs); do
                comments=$(curl -s $path | grep -noP "(<(.*?)-->)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)|(^'.*$)|(^#.*$)" 2>/dev/null)
                if [ ! -z "$comments" ]; then
                        echo -e "\n\n\t${blueColour}---------Path: $path${endColour}" | tee -a comments
                        echo -e "${greenColour}Comments:\n $comments${endColour}" | tee -a comments
                fi
        done
        echo -e "\n[+] All comments fetched, script will finish."
}

if [ $parameter_counter -eq 1 ]; then
        if [ "$(echo $json | grep '.json$')" ]; then #if json file
                if [ -f $json ]; then
                        echo -e "[+] JSON file detected..."
                        directoryListingCheck $json
                        checkLinks
                        findComments
                fi
        elif [ -f $file ]; then
            directoryListingCheck $file
        checkLinks
        findComments
        else
                echo -e "\n\nFile does not exist\n"
        fi
else
        helpPanel
fi

tput cnorm
