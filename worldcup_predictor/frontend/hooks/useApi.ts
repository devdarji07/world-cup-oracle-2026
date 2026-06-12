"use client";
import { useEffect, useState } from "react";
import { api } from "../services/api";
export function useApi<T>(path:string) {
  const [data,setData]=useState<T|null>(null); const [error,setError]=useState("");
  useEffect(()=>{api<T>(path).then(setData).catch((reason)=>setError(String(reason)))},[path]);
  return {data,error,loading:!data&&!error};
}
