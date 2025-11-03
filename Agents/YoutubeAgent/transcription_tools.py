def summarize_transcription(transcription: str, llm) -> str:
    prompt = f"""
Utwórz skrótowe podsumowanie transkrypcji z youtube. Wypisz główne poruszone w transkrypcji tematy w formie podpunktów. 
Podsumowanie ma być krótkie i zwięzłe.
WAŻNE: Nie używaj formatowania markdown, pisz zwykłym tekstem.

Podsumowanie powinno wyglądać następująco:
```
Podsumowanie:
<TREŚĆ_PODSUMOWANIA>

Lokowane produkty:
<LOKOWANE_PRODUKTY>

Kategoria: <KATEGORIA>
```

---
Objaśnienia:

TREŚĆ_PODSUMOWANIA
- skrótowy opis kazdego zagadnienia w transkrypcji
- dla każdego zagadnienia maksymalnie 2-3 zdania
- wybierz maksymalnie 8 głównychzagadnień do podsumowania
- przedstaw je w następującej formie
    Temat 1
    - opis
    - opis

    Temat 2
    - opis

    Temat 3
    - opis

    Przykład:
    Warzywa są źródłem witamin i błonnika
    - codziennie jedzenie warzyw sprzyja zdrowiu
    - błonnik pomaga w trawieniu
    - warzywa powinny stanowić 50% posiłków
    
    Cukier zawarty w owocach jest naturalny i zdrowy
    - owocami można zaspokoić pragnienie i nie trzeba się zastanawiać nad ich nadmiernym spożyciem

KATEGORIA
Skrótowa nazwa kategorii np. edukacja, sport, finanse, sytuacja geopolityczna, etc.

LOKOWANE_PRODUKTY
Tylko nazwy produktów np. XTP, KFD, Freedom 24

Transkrypcja:
{transcription}
"""
    
    try:
        from langchain.schema import HumanMessage
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        result = response.content
        return result if result else "No content returned from API"
        
    except Exception as e:
        error_msg = f"Error generating summary: {e}"
        print(error_msg)
        return error_msg

