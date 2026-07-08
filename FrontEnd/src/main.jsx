import { createRoot } from 'react-dom/client';
import React from 'react';
import {createBrowserRouter, RouterProvider} from 'react-router-dom'
import App from './App';
import AboutPage from './components/AboutPage';
import LoginPage from './components/LoginPage';
import CartPage from './components/CartPage';
import HomePage from './components/HomePage';
import ProfilePage from './components/ProfilePage';
import OrdersPage from './components/Orders';


const router = createBrowserRouter([
  {
    path:'/',
    element:<App />,
    children:[
      {
        path:'/',
        element:<HomePage />,
      },
      {
        path:'/about',
        element:<AboutPage />,
      },
      {
        path:'/login',
        element:<LoginPage />,
      },
      {
        path:'/cart',
        element:<CartPage />,
      },
      {
        path:'/profile',
        element:<ProfilePage />,
      },
      {
        path:'/orders',
        element:<OrdersPage />,
      },
    ]
  }
])

createRoot(document.getElementById('root')).render(
  <RouterProvider router={router} />
)