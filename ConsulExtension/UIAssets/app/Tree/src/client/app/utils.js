export let showShortName = (dataString, strLen)=>{
    if(typeof(dataString) === "string"){
      if(dataString.length > strLen){
        return dataString.substr(0, strLen) + ".."
      }
    return dataString
    }
    else
      return dataString
    
  }


export let  nFormatter = (num) =>{
    if(typeof(num) !== "number"){
      return num
    }
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    }
    return num;
}