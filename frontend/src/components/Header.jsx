import { Link } from 'react-router-dom'
import AuthContext from '../context/AuthContext'
import { useContext } from 'react'
import '../styles/header.css'

const Header = () => {
    let { user, logoutUser } = useContext(AuthContext)

    return (

        <nav className="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
            <div className="container-fluid">
            <ul className="navbar-nav">
            <li className="nav-item">
                <a className="nav-link" href="/">Home</a>
            </li>
            {user && <li className="nav-item navbar-text">{user.username}</li>}
            {user && <li className='nav-item'> 
                <a onClick={logoutUser} className='nav-link' href='#'>Logout</a>
            </li>}

            
            </ul>
            </div>
        </nav>

    )
}

export default Header