export let showShortName = (string, str_len)=>{
    if(string.length > str_len)
      return string.substr(0, str_len) + ".."
    return string
  }