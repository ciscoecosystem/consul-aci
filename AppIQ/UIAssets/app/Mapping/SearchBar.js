import React from 'react'
import './style.css'

class SearchBar extends React.Component {
    constructor(props) {
       super(props)
    }

    render() {
        return (
            <div style={{width : "100%"}}>
                <div className="search-box">
                    <input type="search" className="search-input" ref={this.props.inputRef} onChange={this.props.onChanged} placeholder="Filter by IP or Mac Address"/>
                </div>

            </div>
        )
    }
}

export default SearchBar
