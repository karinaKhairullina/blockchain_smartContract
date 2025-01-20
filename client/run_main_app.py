"""Main app script."""

# ruff: noqa
# from main import main
#
# if __name__ == '__main__':
#     env_file_path = '/Users/ilshatkhairullin/Documents/ems/backend/.env'
#     main()


import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'lottery_client_fastapi:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
