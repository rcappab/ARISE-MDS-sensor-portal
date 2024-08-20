import React from 'react'

interface Props{
    id:string,
    name:string,
    label:string
    defaultvalue: string
}

const FormDateSelector = (props: Props) => {
  return (
    <div className="form-floating">
    <input className="form-control" type="datetime-local"
    id={props.id} name={props.name} 
    defaultValue={props.defaultvalue}/>
    <label htmlFor={props.id}>{props.label}</label>
  </div>
  )
}

export default FormDateSelector