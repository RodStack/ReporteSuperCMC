def compare_with_client_list(temp_db, client_list):
    temp_set = set(temp_db['Codigo_Interno'])
    client_set = set(client_list['Codigo_Interno'])

    discrepancies = {
        'En temp_db pero no aprobado': list(temp_set - client_set),
        'Aprobado pero no en temp_db': list(client_set - temp_set),
        'Diferencias en clasificación': []
    }

    for code in temp_set.intersection(client_set):
        temp_status = temp_db[temp_db['Codigo_Interno'] == code]['Estado_Supervision'].iloc[0]
        client_status = client_list[client_list['Codigo_Interno'] == code]['Estado_Supervision'].iloc[0]
        if temp_status != client_status:
            discrepancies['Diferencias en clasificación'].append((code, temp_status, client_status))

    return discrepancies