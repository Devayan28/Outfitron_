import axios from 'axios'

const api = axios.create({
    // baseURL : "http://localhost:3000/"
    baseURL : "https://musical-funicular-g4qq7j4r467w29jxr-3000.app.github.dev/"
    // baseURL : "https://outfitron-be.vercel.app/"
})

export const login = (props) => {
    
    return api.post('login' , props);

}

export const sendOTP = (email) => {

    return api.post(`sendotp`,{
        email: email
    });

}

export const signUp = (props) => {  

    return api.post(`signup` , props);

}       