import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { connect } from 'react-redux';

class MainMenu extends React.Component {
      render() {
        const { user } = this.props;

        return (
            <nav className='navbar navbar-default'
                 role='navigation'>
              <div className='container-fluid'>
                <div className='navbar-header'>
                  <button type='button'
                          className='navbar-toggle'
                          data-toggle='collapse'
                          data-target='#bs-example-navbar-collapse-1'>
                        <span className='sr-only'>Toggle navigation</span>
                        <span className='icon-bar'></span>
                        <span className='icon-bar'></span>
                        <span className='icon-bar'></span>
                      </button>
                    <NavLink to='/'
                             activeClassName='navbar-brand'>osm-validator</NavLink>
                </div>

                <div className='collapse navbar-collapse'
                     id='bs-example-navbar-collapse-1'>
                  <ul className='nav navbar-nav navbar-right'>
                    <li>
                      <Link to='/' >Main</Link>
                    </li>
                    <li className='dropdown'>
                      <a href='/'
                         className='dropdown-toggle'
                         data-toggle='dropdown'>{ user } <b className='caret'></b>
                      </a>
                      <ul className='dropdown-menu'>
                        <li><Link to='/settings' >Settings</Link></li>
                        <li className='divider'></li>
                        <li><a href='/out'>Exit</a></li>
                      </ul>
                    </li>
                  </ul>
                </div>
              </div>
            </nav>
        );
      }
}

function mapStateToProps (state) {
    return {
        user: state.user
    }
}

export default connect(mapStateToProps)(MainMenu);