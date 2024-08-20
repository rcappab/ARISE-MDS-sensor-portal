import React from 'react'
import { useContext, useEffect, useState } from 'react'
import AuthContext from '../context/AuthContext';
import Gallery from '../components/Gallery';

const HomePage = () => {

    const {user} = useContext(AuthContext);

    return (
        user  ? (
        <div>
           <Gallery />
        </div>
        ):(
        <div>
            <p>You are not logged in, redirecting...</p>
        </div>
        )

    )
}

export default HomePage