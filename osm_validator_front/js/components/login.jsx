import React from 'react';

export default class Login extends React.Component {
    render() {
        return (
            <div className='container'>
              <div className='row'>

                <div className='col-xs-12 text-center'>
                  <h2>osm-validator</h2>
                </div>

                <div className='col-xs-12'>
                  <img src='/static/img/avatar.jpeg'
                       alt='Avatar'
                       style={{margin: '0 auto'}}
                       className='img-responsive' />
                </div>

                <div className='col-xs-12 text-center'>
                  <a className='btn btn-default'
                     href='/oauth/login'
                     role='button'>Login through www.openstreetmap.org</a>
                </div>

              </div>
            </div>
        );
    }
}
