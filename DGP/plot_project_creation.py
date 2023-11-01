import pandas as pd
import matplotlib.pyplot as plt

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:cyan', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:brown']

#file = '4.GroupsFinal.csv'

csv_file_names = ['5G', '6G', 'Artificial Intelligence', 'Augmented Reality', 'blockchain',
                  'Contratos Inteligentes', 'digital twin', 'gemeos digitais',
                  'Inteligencia Artificial', 'metaverse', 'metaverso', 'Realidade Aumentada',
                  'Realidade Mista', 'Smart Contracts', 'Virtual Reality',
                   'Computação de Borda', 'Computação na Borda', 'Edge Computing',
                   'fake news', 'misinformation', 'rumor', 'disinformation', 'desinformação']
assuntos = {
    '5G': '5G e Pós-5G',
    '6G': '5G e Pós-5G',
    
    'Artificial Intelligence' : 'Inteligencia Artificial',
    'Inteligencia Artificial' : 'Inteligencia Artificial',
    
    'Augmented Reality' : 'Imersividade',
    'Realidade Aumentada' : 'Imersividade',
    'Realidade Mista' : 'Imersividade',
    'Virtual Reality' : 'Imersividade',
    
    'blockchain' : 'Blockchain',
    'Contratos Inteligentes' : 'Blockchain',
    'Smart Contracts' : 'Blockchain',
    
    'digital twin' : 'Gêmeos Digitais',
    'gemeos digitais' : 'Gêmeos Digitais',
    
    'metaverse' : 'Metaverso',
    'metaverso' : 'Metaverso',
    
    'Computação de Borda' : 'Computação de Borda',
    'Computação na Borda' : 'Computação de Borda',
    'Edge Computing' : 'Computação de Borda',
    
    'fake news' : 'Fake news', 
    'misinformation' : 'Fake news', 
    'rumor' : 'Fake news', 
    'disinformation' : 'Fake news',
    'desinformação' : 'Fake news'
    
}


def concatenate_csv_files_and_insert_assunti_field(csv_files):
    df_list = []
    for item in csv_files:
        df = pd.read_csv(item + '.csv', sep=";")
        # Drop duplicates
        df = df.drop_duplicates(subset='Grupo', keep="first")
        df['Assunto'] = assuntos[item]
        df_list.append(df)

    total_df  = pd.concat(df_list, ignore_index=True)
    return total_df
    

def generate_incremental_array(first_number, last_number, interval):
    array = []
    current_number = first_number
    
    while current_number <= last_number:
        array.append(current_number)
        current_number += interval
    
    return array

def plot(csv_files):
    # Read the CSV file into a DataFrame
    df = concatenate_csv_files_and_insert_assunti_field(csv_files)
    
    # Plotar apenas grupos de pesquisa apos 2012
    df = df[df['Ano Formação'] >= 2012] 
    
    # Convert 'AnoInicio' column to datetime type
    df['Ano Formação'] = pd.to_datetime(df['Ano Formação'], format='%Y', errors='coerce')
    
    # Group the projects by year and 'Assunto', and count the quantity
    projects_by_year_subject = df.groupby([df['Ano Formação'].dt.year, 'Assunto'])['Grupo'].count().unstack()
    
    # Remove Nan values and cumulate the values
    projects_by_year_subject =  projects_by_year_subject.cumsum()
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    #plt.yscale("log")
    
    # Plot each 'Assunto' as a separate line
    for i, column in enumerate(projects_by_year_subject.columns):
        plt.plot(projects_by_year_subject.index, projects_by_year_subject[column], marker='o', linestyle='--', color=colors[i], label=column)
    
    plt.xlabel('Ano de criação')
    plt.ylabel('Quantidade')
    plt.title('Grupos de pesquisa acumulativos')
    plt.legend()
    plt.xticks(generate_incremental_array(2012, 2023, 1), rotation=0)
    #plt.yticks(fontsize=14)
    plt.savefig('plots/grupos_de_pesquisa_dgp.pdf', dpi=600, bbox_inches='tight')
    #plt.show()
    
if __name__ == "__main__":
    plot(csv_file_names)