import os
import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter


api =st.secrets['claude_key']



from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model='claude-3-haiku-20240307', api_key = api)





# Function to load documents
# Improved error handling in document loading
def load_documents(file):
    try:
        name, extension = os.path.splitext(file)
        if extension == ".pdf":
            loader = PyPDFLoader(file)
        elif extension == ".docx":
            loader = Docx2txtLoader(file)
        else:
            st.error("Document format is not supported!")
            return None
        return loader.load()
    except Exception as e:
        st.error(f"Failed to load document: {str(e)}")
        return None

# Function to chunk data
def chunk_data(data, chunk_size=1000):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
    return text_splitter.split_documents(data)


def first_prompt(job, documents,position):
    template = """
             As an expert ATS scanner with specialized expertise in {role} and a thorough understanding of ATS functionality, 
             your primary task is to meticulously assess the provided resume against the job requirements. Begin by scanning 
             both the resume and the requirements to identify and compare relevant keywords. 
             
             1. **Percentage Match**: Calculate the percentage match based on the number of keywords in the job description 
             that are also present in the resume. Use the formula (Number of Matching Keywords / Total Keywords in the Job 
             Description) * 100 to determine the match percentage.
             
             2. **Missing Keywords**: List any crucial keywords from the job description that are not found in the resume. 
             These are the areas where the candidate may lack the required skills or experience.
             
             
              Please format your analysis and suggestions as follows:
              - Percentage Match: the Calculated Percentage %  of matched keywords
              - Missing Keywords: [List of missing keywords]



            {requirements}

             {resume}
             
             
              """

    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm  | StrOutputParser()
    
    answer = chain.invoke({
    "requirements" :job, 
    "resume" : documents,
    "role": position
    
    })
    
    return answer



def second_prompt(job, documents,position):
   
    template = """
               As an advanced ATS scanner with specialized expertise in {role} and comprehensive knowledge of ATS
               functionality, your primary task is to thoroughly assess the provided resume against the job requirements. After
               evaluating the resume, please provide detailed examples of potential improvements that could enhance the 
               resume's alignment with  the job description. This should include recommendations for adding or emphasizing 
               specific skills, experiences, or qualifications that are crucial for the role but currently missing or 
               understated in the resume.

   

            {requirements}

             {resume}
             
             
             1. **Initial Assessment**: Analyze the resume to determine how well it matches the specified job requirements. 
             Identify any areas where the resume meets the expectations and areas where it falls short.
             
             
             2. **Improvement Suggestions**: Based on your assessment, suggest specific changes or additions to the resume that
             could improve its alignment with the job requirements. These suggestions should focus on tangible elements such 
             as skills, experiences, certifications, or educational qualifications that are relevant to the role.


              3. **Detailed Examples**: Provide concrete examples of how the suggested improvements could be implemented. For
              instance, if the job requires strong project management skills and the resume only briefly mentions project
              management, suggest that the candidate elaborates on specific projects they managed, detailing the scope, the
              outcomes, and the skills they applied.


              Please format your analysis and suggestions as follows:
              - Initial Assessment: [Summary of how the resume matches the job requirements]
              - Improvement Suggestions: [List of detailed suggestions for enhancing the resume]
              - Detailed Examples: [Examples of how to implement the improvements]
             
              """

    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm  | StrOutputParser()
    
    answer = chain.invoke({
    "requirements" :job, 
    "resume" : documents,
    "role": position
    
    })
    
    return answer


def clear_session():
    
    
    if 'answer1' in st.session_state:
        del st.session_state['answer1']
        del st.session_state['answer2']
        

    
# Streamlit app
if __name__ == "__main__":
    st.title("Applicant Tracking System")
    #st.subheader("Plug in your data source")
    
    
    position = st.text_input("Job role: ")
    requirements =st.text_area("Job Description: ")
    
  
    
    uploaded_file = st.file_uploader("Upload your resume:", type=[ "docx", "pdf"])
    if uploaded_file:
        add_data = st.button('Upload Resume', on_click=clear_session)
        if add_data:
                with st.spinner('Reading and processing file ...'):
                    
                    
                    # writing the file from RAM to the current directory on disk  
                    bytes_data = uploaded_file.read()
                    file_name = os.path.join('./', uploaded_file.name)
                    with open(file_name, 'wb') as f: #write file to name
                        f.write(bytes_data)
                        
                        
                    ## Load the Content from the file  
                    datas = load_documents(file_name)
                
                    cv = chunk_data(datas, chunk_size=1000)
                    
                    
                    st.success('Resume has been uploaded.')
                    st.session_state.resume = cv
                    
                    
                    
    st.divider()
    
    
    submit1 = st.button("Percentage and Missing Keywords")
    if submit1:
        if 'resume' in st.session_state:
            resume = st.session_state.resume
            

            if 'answer1'in st.session_state:
                first_answer = st.session_state.answer1
                
                # text area widget for the LLM answer
                st.text_area('Percentage and Missing Keywords: ', value=first_answer,height=150 )
                
            else:
                answer1 = first_prompt(requirements,resume, position)
                st.session_state.answer1 = answer1
                first_answer = st.session_state.answer1
            # text area widget for the LLM answer
                st.text_area('Percentage and Missing Keywords: ', value=first_answer, height=150)
    
    
    st.divider()
    
    
    submit2 = st.button("Evaluation and Improvement Suggestions")
    if submit2:
        if 'resume' in st.session_state:
            
            resume = st.session_state.resume
            
            if 'answer2'in st.session_state:
                second_answer = st.session_state.answer2
                
                # text area widget for the LLM answer
                st.text_area('Evaluation and Improvement Suggestions: ', value=second_answer,height=150)
                
            else:
                answer2 = second_prompt(requirements,resume, position)
                st.session_state.answer2 = answer2
                second_answer = st.session_state.answer2
            # text area widget for the LLM answer
                st.text_area('Evaluation and Improvement Suggestions: ', value=second_answer,height=150)
            
