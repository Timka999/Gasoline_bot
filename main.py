from bot import Bot

with open('TOKEN.txt', 'r') as file:
    TOKEN = file.read().strip()

def main() -> None:
    
    my_bot = Bot(TOKEN)
    my_bot.run()

if __name__ == '__main__':
    
    main()
   