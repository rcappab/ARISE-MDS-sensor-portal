import React, {useState, useEffect} from 'react'

const JSONInput = () => {
const [JSONtext, setJSONtext] = useState('{}')
const [inputFields, setInputFields] = useState([   
])

const handleJSONChange = () => {
    let newObj = inputFields.reduce((obj, item) => ({...obj, [item.key]: item.value}) ,{});
    setJSONtext(JSON.stringify(newObj))
}

const handleFormChange = (index, event) => {
    let data = [...inputFields];
    data[index][event.target.name] = event.target.value;
    setInputFields(data);
    
}

const addFields = (e) => {
    e.preventDefault();
    let newfield = { key: '', value: '' }
    setInputFields([...inputFields, newfield])
    
}

const removeFields = (index) => {
    let data = [...inputFields];
    data.splice(index, 1)
    setInputFields(data)   
}

useEffect(() => {
    handleJSONChange()
}, [inputFields])


  return (
    <div>
    <textarea name='extra_info' value={JSONtext} readOnly={true}></textarea >
    <button onClick={addFields}>Add More..</button>

    {inputFields.map((input, index) => {
        return (
            <div key={index}>
            <input
                name='key'
                placeholder='key'
                value={input.key}
                form=""
                onChange={event => handleFormChange(index, event)}
            />:
            <input
                name='value'
                placeholder='value'
                value={input.value}
                form=""
                onChange={event => handleFormChange(index, event)}
                
            />
            <button onClick={(e) => {e.preventDefault();removeFields(index)}}>Remove</button>

            </div>
        )
        })}
        </div>
  )
}

export default JSONInput;