import pandas as pd
import streamlit as st
import pickle
import requests


dic={}
History=[]
# making dic and History as session state variables so that they will not be refreshed every time
if "dic" not in st.session_state:
    st.session_state.dic={}
if "History" not in st.session_state:
    st.session_state.History=[]
def add_userdata(username, password):
    st.session_state.dic[username]=password

#checking log in
def login_user(username, password):
    for i in st.session_state.dic.keys():
        if username==i and st.session_state.dic[username]==password:
            return True
    return False

#loaded files after processing in jupyter for the recomendation
movie_lst = pickle.load(open('Movie_names_original.pkl', 'rb'))
movie_lst = pd.DataFrame(movie_lst)
similarity = pickle.load(open('similarity_matrix_original.pkl', 'rb'))
images_url = pickle.load(open('images_url1.pkl', 'rb'))

#baseurl for finding the shows using the given name
baseurl='https://api.tvmaze.com/search/shows?q='

def main():
    #sidebar menu for login signin and home page for the recomendation system
    menu = ['Home', 'Login', 'Sign Up']
    choice = st.sidebar.selectbox("MENU", menu)
    if choice == 'Home':
        movie_name=st.text_input("Enter the movie name you want to search")
        if st.button("search"):
            #spliting the window into 3 columns 
            col1,col2=st.columns([1,4])
            #getting the response form the api in the json format
            response=requests.get(baseurl+movie_name).json()
            res=response[0]
            #finding the image url for the medium sized image as it is dictionary accessing using keys
            image=res['show']['image']['medium']
            col1.image(image)
            #similarly finding the name
            name = res['show']['name']
            col2.write(name)
            #finding the runtime of rthe given movie in the tv maze api
            runtime = res['show']['runtime']
            col2.write('Runtime :'+str(runtime))
            language = res['show']['language']
            col2.write("Language: " + language)
    #login page functions
    elif choice == 'Login':
        user_name = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input('Password', type='password')
        if st.sidebar.checkbox('Login'):
            #create_usertable()
            #result = login_user(user_name, password)
            #if password=='1234':
            
            result=login_user(user_name,password)
            #st.write(result)
            if result:
                #if result is true when the data is already found in the dict the request is allowed
                st.success('Logged in as {}'.format(user_name))
                st.title('Search for Best Movies')
                #selecting movies form the list of movies from the plk file that has been used  and processed in th jupyter
                selected_movie_option = st.selectbox('Choose a movie form list', movie_lst['name'].values)
                #spliting the window into 3 equal columns
                col1, col2, col3 = st.columns(3)
                if col1.button('recommend'):
                    #adding to the history if the movie is not present
                    if selected_movie_option not in st.session_state.History:
                        st.session_state.History.append(selected_movie_option) 
                    #final movie list (5 movies)
                    final_values = recomend(selected_movie_option)
                    #finding the image url from the json data that has been returned from the api
                    response=requests.get(baseurl+selected_movie_option).json()
                    #getting the show values
                    res=response[0]
                    st.write(selected_movie_option)
                    image = res['show']['image']['medium']
                    st.image(image)
                    st.title("Top Recomendations for you based on your choice")
                    #final recomended movies
                    for i in final_values:
                        st.write(i)
                        response = requests.get(baseurl + i).json()
                        res = response[0]
                        image = res['show']['image']['medium']
                        st.image(image)

                #displaying the history information
                if col2.button('Show History'):
                    for i in st.session_state.History:
                        col2.write(i)
                    if(st.session_state.History==[]):
                        col2.write("Nothing to show up!!")
                #clearing the history 
                if col3.button('Clear History'):
                    st.session_state.History=[]
            else:
                st.info("Incorrect Username/Password")
                
    #creating an user account 
    elif choice == 'Sign Up':
        #in the main page
        st.subheader("Create New Account")
        new_user = st.text_input("UserName")
        new_password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            if not login_user(new_user,new_password):
                add_userdata(new_user, new_password)
                st.success("You Have Created an account")
                st.info("Go back to log in page")
            else:
                st.info("Account already exists")


# def findurl(selected_movie_option):
# movie_names=recomend(selected_movie_option)
# img_url=[]
# for i in movie_names:
#  t = images_url[images_url['name'] == i]
#  nnn = t.values[0]
#  img_url.append(nnn[1]['medium'])
# return  images_url

#recomendation algorithm
def recomend(movie):
    # finding index so we cant lose it
    movie_index = movie_lst[movie_lst['name'] == movie].index[0] 
    # finding distances array
    distances = similarity[movie_index]  
    recomend_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recomended_movies_lst = []
    # recomended_movie_images=[]
    for i in recomend_list:
        recomended_movies_lst.append(movie_lst.iloc[i[0]][1])
        # recomended_movie_images.append()
    return recomended_movies_lst

if __name__ == '__main__':
    main()
