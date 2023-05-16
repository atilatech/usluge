import openai

from telebot.credentials import OPEN_AI_API_KEY

# Set up OpenAI API credentials
openai.api_key = OPEN_AI_API_KEY


def find_service_provider(prompt):

    # Make the API call to OpenAI
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt='Prompt: Reply the following message:' + prompt + '\n\n using the following information' + services_data,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Process the API response
    if response.choices:
        return response.choices[0].text.strip()
    else:
        return None


services_data = """
name,category,phone,kategorija,opis,grad,description,Instagram
Dzoli company,painter,067 305 270,moler,KREČENJE - MOLERSKI RADOV,Crna Gora,,
A&R Moler krecenje,painter,066 133 740,moler,"Krečenje - farbanje - gletovanje - postavljanje tapeta - dekorativne tehnike - čišćenje, demit fasade",Crna Gora,,
miki design,painter,063 487 403,moler,"Dekorativni radovi, gletovanje, krečenje, molerske usluge, adaptacija, gipsarski radovi, demit fasade, stiropol fasade",Podgorica,,
DAZMONT,painter,068 007 110,moler,Moleraj,Podgorica,,
M&FIK,painter,069 609 171,moler,MOLERSKE USLUGE - GLETOVANJE - FARBANJE - DEKORATIVNE TEHNIKE - DEMIT FASADE,Podgorica,,
Molerski radovi 2,painter,067 016 109 / 069 720 808,moler,"MOLERAJ, KRECENJE, FARBANJE, GLETOVANJE",Podgorica,,
Darko,painter,67482372,moler,"Radim uglavnom krečenje stanova, decorative tehnike i demit fasade",Podgorica,,
Moler bato,painter,069 848 747,moler,,Budva Tivat Kotor,,
Molerski radovi 3,painter,69 720 808,moler,,Budva ,,
Molerski radovi 4,painter,068 074 170,moler,"Izrada fasada, gipsni radovi, gletovanje, dekorativne tehnike",Podgorica,,
Molerski radovi dekoracije,painter,068 364 234,moler,"Dekorativne tehnike, molerski radovi, gipsani radovi",Podgorica,,
Molerski radovi 5,painter,,moler,,Crna Gora,,https://instagram.com/molerski_radovi_10?igshid=MTIyMzRjYmRlZg==
Molerski radovi,,068 404 565,,,,,
"""